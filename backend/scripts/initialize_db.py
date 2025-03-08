"""Initialize the vector database."""
import os
import sys

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.vector_db import VectorDBService

def main():
    """Initialize the vector database."""
    print("Initializing vector database...")
    vector_db = VectorDBService()
    success = vector_db.index_documents()
    
    if success:
        print("Vector database initialized successfully!")
    else:
        print("Failed to initialize vector database.")

if __name__ == "__main__":
    main()