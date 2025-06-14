"""Service de base de données vectorielle avec FAISS et embeddings locaux."""
import os
import pickle
import numpy as np
from services.document_ocr_service import DocumentOCRService
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
        os.makedirs(persist_directory, exist_ok=True)
        
        self.index_path = os.path.join(persist_directory, "faiss_index")
        
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
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
        try:
            self.ocr_service = DocumentOCRService()
            print("OCR service initialized for document processing")
        except Exception as e:
            print(f"Warning: OCR service could not be initialized: {e}")
            self.ocr_service = None
    
    def _process_document_with_ocr(self, file_path: str) -> str:
        """
        Process a document and extract text from images if OCR is available.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text from images, or empty string if no OCR or no text found
        """
        if not self.ocr_service:
            return ""
        
        try:
            if self.ocr_service.should_process_for_images(file_path):
                print(f"Checking for images in: {file_path}")
                
                ocr_text = self.ocr_service.process_document_with_ocr(file_path)
                
                if ocr_text.strip():
                    print(f"Extracted {len(ocr_text)} characters from images in {file_path}")
                    return ocr_text
                else:
                    print(f"No text found in images within {file_path}")
            
        except Exception as e:
            print(f"Error during OCR processing of {file_path}: {e}")
        
        return ""
    
    def _get_loader_for_file(self, file_path):
        """
        Obtenir le chargeur approprié selon le type de fichier.
        Modified to include OCR processing for documents with images.
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.pdf':
                print(f"Utilisation de PyPDFLoader pour {file_path}")
                
                ocr_text = self._process_document_with_ocr(file_path)
                
                loader = PyPDFLoader(file_path)
                
                if ocr_text:
                    setattr(loader, '_ocr_text', ocr_text)
                
                return loader
                
            elif file_extension in ['.docx', '.doc']:
                print(f"Utilisation de Docx2txtLoader pour {file_path}")
                
                ocr_text = self._process_document_with_ocr(file_path)
                
                loader = Docx2txtLoader(file_path)
                
                if ocr_text:
                    setattr(loader, '_ocr_text', ocr_text)
                
                return loader
                
            elif file_extension == '.csv':
                print(f"Utilisation de CSVLoader pour {file_path}")
                return CSVLoader(file_path)
            elif file_extension == '.json':
                print(f"Utilisation de JSONLoader pour {file_path}")
                return JSONLoader(file_path=file_path, jq_schema='.', text_content=False)
            else:
                try:
                    print(f"Utilisation de TextLoader (utf-8) pour {file_path}")
                    return TextLoader(file_path, encoding='utf-8')
                except Exception as e:
                    print(f"Erreur avec encodage utf-8 pour {file_path}: {e}")
                    try:
                        print(f"Utilisation de TextLoader (latin-1) pour {file_path}")
                        return TextLoader(file_path, encoding='latin-1')
                    except Exception as e2:
                        print(f"Échec de tous les encodages pour {file_path}: {e2}")
                        return None
        except Exception as e:
            print(f"Erreur lors de la création du chargeur pour {file_path}: {e}")
            return None

    def index_documents(self, documents_directory="./knowledge"):
        """Indexer les documents du répertoire spécifié avec OCR intégré."""
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
                                
                                # Check if we have OCR text to append
                                if hasattr(loader, '_ocr_text') and loader._ocr_text:
                                    print(f"Appending OCR text to documents from {file_path}")
                                    
                                    # Create a new document with OCR text
                                    from langchain.schema import Document
                                    ocr_document = Document(
                                        page_content=f"=== EXTRACTED TEXT FROM IMAGES ===\n\n{loader._ocr_text}",
                                        metadata={
                                            "source": file_path,
                                            "type": "ocr_extracted",
                                            "original_file": os.path.basename(file_path)
                                        }
                                    )
                                    documents.append(ocr_document)
                                
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
    

    def index_single_document(self, file_path):
        """Index a single document without clearing the entire database."""
        try:
            print(f"Indexing single document: {file_path}")
            
            loader = self._get_loader_for_file(file_path)
            if not loader:
                print(f"No suitable loader found for {file_path}")
                return False
            
            documents = loader.load()
            print(f"Loaded {len(documents)} document segments from {file_path}")
            
            if not documents:
                print(f"No content extracted from {file_path}")
                return False
            
            if hasattr(self, 'ocr_service') and self.ocr_service:
                try:
                    if self.ocr_service.should_process_for_images(file_path):
                        print(f"Applying OCR to extract text from images in {file_path}")
                        ocr_text = self.ocr_service.process_document_with_ocr(file_path)
                        
                        if ocr_text.strip():
                            from langchain.schema import Document
                            ocr_doc = Document(
                                page_content=ocr_text,
                                metadata={
                                    "source": file_path,
                                    "extraction_method": "OCR",
                                    "file_name": os.path.basename(file_path)
                                }
                            )
                            documents.append(ocr_doc)
                            print(f"Added OCR-extracted text ({len(ocr_text)} characters)")
                except Exception as ocr_error:
                    print(f"OCR processing failed for {file_path}: {ocr_error}")
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)
            print(f"Split into {len(splits)} chunks")
            
            if self.db is None:
                print("Creating new vector database")
                self.db = FAISS.from_documents(splits, self.embeddings)
            else:
                print("Adding to existing vector database")
                new_db = FAISS.from_documents(splits, self.embeddings)
                self.db.merge_from(new_db)
            
            self.db.save_local(self.index_path)
            print(f"Successfully indexed single document: {file_path}")
            
            return True
        
        except Exception as e:
            print(f"Error indexing single document {file_path}: {e}")
            import traceback
            traceback.print_exc()
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