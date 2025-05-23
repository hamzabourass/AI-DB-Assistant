"""Service de base de données vectorielle avec FAISS et embeddings locaux."""
import os
import pickle
import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Import specialized document loaders
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import CSVLoader
from langchain_community.document_loaders import JSONLoader

from dotenv import load_dotenv

load_dotenv()

class VectorDBService:
    """Service pour gérer les opérations de base de données vectorielle avec FAISS."""
    
    def __init__(self, persist_directory="./database/vector_db"):
        """Initialiser le service de base de données vectorielle."""
        # Créer le répertoire s'il n'existe pas
        os.makedirs(persist_directory, exist_ok=True)
        
        # Chemin pour stocker l'index FAISS
        self.index_path = os.path.join(persist_directory, "faiss_index")
        
        # Initialiser le modèle d'embedding (modèle local, pas d'API nécessaire)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Essayer de charger la base de données existante
        if os.path.exists(os.path.join(self.index_path, "index.faiss")):
            try:
                self.db = FAISS.load_local(
                    self.index_path, 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
                print(f"Base de données vectorielle existante chargée")
            except Exception as e:
                print(f"Erreur lors du chargement de la base de données existante : {e}")
                self.db = None
        else:
            self.db = None
            print("Aucune base de données vectorielle existante trouvée")
    
    def _get_loader_for_file(self, file_path):
        """
        Obtenir le chargeur approprié selon le type de fichier.
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            # Sélectionner le chargeur approprié selon l'extension
            if file_extension == '.pdf':
                print(f"Utilisation de PyPDFLoader pour {file_path}")
                return PyPDFLoader(file_path)
            elif file_extension in ['.docx', '.doc']:
                print(f"Utilisation de Docx2txtLoader pour {file_path}")
                return Docx2txtLoader(file_path)
            elif file_extension == '.csv':
                print(f"Utilisation de CSVLoader pour {file_path}")
                return CSVLoader(file_path)
            elif file_extension == '.json':
                print(f"Utilisation de JSONLoader pour {file_path}")
                return JSONLoader(file_path=file_path, jq_schema='.', text_content=False)
            else:
                # Pour les fichiers texte et autres formats
                try:
                    # Tenter d'utiliser l'encodage utf-8
                    print(f"Utilisation de TextLoader (utf-8) pour {file_path}")
                    return TextLoader(file_path, encoding='utf-8')
                except Exception as e:
                    print(f"Erreur avec encodage utf-8 pour {file_path}: {e}")
                    try:
                        # Si utf-8 échoue, essayer avec latin-1 (plus permissif)
                        print(f"Utilisation de TextLoader (latin-1) pour {file_path}")
                        return TextLoader(file_path, encoding='latin-1')
                    except Exception as e2:
                        print(f"Échec de tous les encodages pour {file_path}: {e2}")
                        return None
        except Exception as e:
            print(f"Erreur lors de la création du chargeur pour {file_path}: {e}")
            return None

    def index_documents(self, documents_directory="./knowledge"):
        """Indexer les documents du répertoire spécifié."""
        # Créer le répertoire s'il n'existe pas
        os.makedirs(documents_directory, exist_ok=True)
        
        try:
            # Liste des extensions de fichiers à traiter
            extensions = ['.txt', '.md', '.csv', '.json', '.xml', '.html', '.pdf', '.docx', '.doc']
            
            # Liste pour stocker tous les documents
            all_documents = []
            
            # Parcourir tous les fichiers dans le répertoire
            for root, dirs, files in os.walk(documents_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_extension = os.path.splitext(file_path)[1].lower()
                    
                    # Ne traiter que les extensions connues
                    if file_extension in extensions:
                        try:
                            # Obtenir le chargeur pour ce fichier
                            loader = self._get_loader_for_file(file_path)
                            if loader:
                                # Charger les documents
                                documents = loader.load()
                                all_documents.extend(documents)
                                print(f"Chargé {len(documents)} segments depuis {file_path}")
                        except Exception as e:
                            print(f"Erreur lors du chargement de {file_path}: {e}")
            
            if not all_documents:
                print(f"Aucun document trouvé dans {documents_directory}")
                return False
            
            print(f"Chargé {len(all_documents)} documents au total")
            
            # Diviser les documents en chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(all_documents)
            
            print(f"Divisé en {len(splits)} chunks")
            
            # Créer un nouvel index FAISS
            self.db = FAISS.from_documents(splits, self.embeddings)
            
            # Sauvegarder l'index
            self.db.save_local(self.index_path)
            
            print(f"Base de données vectorielle sauvegardée dans {self.index_path}")
            
            return True
        
        except Exception as e:
            print(f"Erreur lors de l'indexation des documents : {e}")
            return False
    
    def reload_index(self):
        """Recharge l'index depuis le disque."""
        try:
            if os.path.exists(os.path.join(self.index_path, "index.faiss")):
                self.db = FAISS.load_local(
                    self.index_path, 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
                print("Index vectoriel rechargé avec succès")
                return True
            return False
        except Exception as e:
            print(f"Erreur lors du rechargement de l'index: {e}")
            return False
        
    def clear_and_reindex(self, documents_directory="./knowledge"):
        """Effacer l'index existant et réindexer tous les documents."""
        try:
            # Supprimer les fichiers d'index existants
            if os.path.exists(os.path.join(self.index_path, "index.faiss")):
                os.remove(os.path.join(self.index_path, "index.faiss"))
            
            if os.path.exists(os.path.join(self.index_path, "index.pkl")):
                os.remove(os.path.join(self.index_path, "index.pkl"))
            
            # Réindexer les documents
            return self.index_documents(documents_directory)
        
        except Exception as e:
            print(f"Erreur lors de la réindexation : {e}")
            return False
    
    def search(self, query, k=4):
        """Rechercher des documents pertinents en fonction de la requête avec métadonnées complètes."""
        try:
            if self.db is None:
                print("Base de données vectorielle non initialisée. Indexation des documents...")
                success = self.index_documents()
                if not success:
                    return []
            
            docs_and_scores = self.db.similarity_search_with_score(query, k=k)
            
            enhanced_docs = []
            for doc, score in docs_and_scores:
                source_path = doc.metadata.get("source", "Source inconnue")
                
                if os.path.exists(source_path):
                    file_stats = os.stat(source_path)
                    file_name = os.path.basename(source_path)
                    file_extension = os.path.splitext(file_name)[1].lower()
                    
                    doc.metadata.update({
                        "file_name": file_name,
                        "file_extension": file_extension,
                        "file_size_bytes": file_stats.st_size,
                        "last_modified": file_stats.st_mtime,
                        "similarity_score": float(score)
                    })
                else:
                    doc.metadata["similarity_score"] = float(score)
                
                enhanced_docs.append(doc)
            
            return enhanced_docs
        except Exception as e:
            print(f"Erreur lors de la recherche de documents : {e}")
            return []