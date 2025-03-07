"""Vector Database Service for storing and retrieving document embeddings."""
import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from dotenv import load_dotenv

load_dotenv()

class VectorDBService:
    """Service for managing vector database operations."""
    
    def __init__(self, persist_directory="./database/vector_db"):
        """Initialize the Vector DB service."""
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Use the same API key as the LLM service
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set in .env file")
        
        # Initialize the embedding model
        self.embeddings = OpenAIEmbeddings(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key
        )
        
        # Check if vector database exists
        self.persist_directory = persist_directory
        if os.path.exists(persist_directory) and os.listdir(persist_directory):
            # Load existing database
            self.db = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings
            )
            print(f"Loaded existing vector database with {self.db._collection.count()} documents")
        else:
            # Create new database
            self.db = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings
            )
            print("Created new vector database")
    
    def index_documents(self, documents_directory="./knowledge"):
        """
        Index documents from the specified directory.
        
        Args:
            documents_directory: Directory containing knowledge base documents
        """
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
            
            # Add documents to vector store
            self.db.add_documents(splits)
            
            # Persist the database
            self.db.persist()
            
            return True
        
        except Exception as e:
            print(f"Error indexing documents: {e}")
            return False
    
    def search(self, query, k=4):
        """
        Search for relevant documents based on the query.
        
        Args:
            query: The search query
            k: Number of documents to retrieve
            
        Returns:
            List of retrieved documents
        """
        try:
            docs = self.db.similarity_search(query, k=k)
            return docs
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []

# Example usage
if __name__ == "__main__":
    # Initialize vector database service
    vector_db = VectorDBService()
    
    # Index documents
    vector_db.index_documents()
    
    # Test search
    results = vector_db.search("What is database normalization?")
    
    for doc in results:
        print(f"Content: {doc.page_content[:100]}...")
        print(f"Source: {doc.metadata.get('source', 'Unknown')}")
        print("-" * 50)