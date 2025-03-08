"""Vector Database Service with FAISS and local embeddings."""
import os
import pickle
import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from dotenv import load_dotenv

load_dotenv()

class VectorDBService:
    """Service for managing vector database operations with FAISS."""
    
    def __init__(self, persist_directory="./database/vector_db"):
        """Initialize the Vector DB service."""
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Path to store the FAISS index
        self.index_path = os.path.join(persist_directory, "faiss_index")
        
        # Initialize the embedding model (local model, no API needed)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Try to load existing database
        if os.path.exists(os.path.join(self.index_path, "index.faiss")):
            try:
                self.db = FAISS.load_local(
                    self.index_path, 
                    self.embeddings, 
                    allow_dangerous_deserialization=True  # Add this parameter
                )
                print(f"Loaded existing vector database")
            except Exception as e:
                print(f"Error loading existing database: {e}")
                self.db = None
        else:
            self.db = None
            print("No existing vector database found")
    
    def index_documents(self, documents_directory="./knowledge"):
        """Index documents from the specified directory."""
        # Create directory if it doesn't exist
        os.makedirs(documents_directory, exist_ok=True)
        
        try:
            # Load documents from directory
            loader = DirectoryLoader(
                documents_directory,
                glob="**/*.txt",
                loader_cls=TextLoader
            )
            documents = loader.load()
            
            if not documents:
                print(f"No documents found in {documents_directory}")
                return False
            
            print(f"Loaded {len(documents)} documents")
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)
            
            print(f"Split into {len(splits)} chunks")
            
            # Create new FAISS index
            self.db = FAISS.from_documents(splits, self.embeddings)
            
            # Save the index
            self.db.save_local(self.index_path)
            
            print(f"Saved vector database to {self.index_path}")
            
            return True
        
        except Exception as e:
            print(f"Error indexing documents: {e}")
            return False
    
    def search(self, query, k=4):
        """Search for relevant documents based on the query."""
        try:
            if self.db is None:
                print("Vector database not initialized. Indexing documents...")
                success = self.index_documents()
                if not success:
                    return []
            
            docs = self.db.similarity_search(query, k=k)
            return docs
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []