"""Service for inspecting vector database contents."""
import os
import uuid
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

class VectorDBInspector:
    """Service for inspecting vector database contents."""
    
    def __init__(self, persist_directory="./database/vector_db"):
        """Initialize the Vector DB Inspector service."""
        self.persist_directory = persist_directory
        
        self.index_path = os.path.join(persist_directory, "faiss_index")
        
        print(f"Looking for vector database in: {os.path.abspath(self.index_path)}")
        print(f"Files in directory: {os.listdir(self.index_path) if os.path.exists(self.index_path) else 'Directory not found'}")
        
        if not os.path.exists(os.path.join(self.index_path, "index.faiss")):
            print(f"index.faiss not found at {os.path.join(self.index_path, 'index.faiss')}")
            raise ValueError(f"Vector database file index.faiss not found in {self.index_path}")
        
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        try:
            self.db = FAISS.load_local(
                self.index_path, 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            print(f"Successfully loaded vector database with {len(self.db.docstore._dict)} documents")
        except Exception as e:
            print(f"Error loading vector database: {e}")
            raise ValueError(f"Error loading vector database: {e}")
    def get_document_count(self):
        """Get the number of documents in the vector database."""
        try:
            return len(self.db.docstore._dict)
        except:
            return 0
    
    def get_all_documents(self, limit=100, offset=0):
        """Get all documents in the vector database with pagination."""
        try:
            all_ids = list(self.db.docstore._dict.keys())
            
            paginated_ids = all_ids[offset:min(offset+limit, len(all_ids))]
            
            if not paginated_ids:
                return []
            
            documents = []
            for doc_id in paginated_ids:
                try:
                    doc = self.db.docstore._dict.get(doc_id)
                    if doc:
                        metadata = {}
                        for k, v in doc.metadata.items():
                            if isinstance(v, (str, int, float, bool, list, dict, type(None))):
                                metadata[k] = v
                            else:
                                metadata[k] = str(v)
                        
                        documents.append({
                            "id": str(doc_id),
                            "content": doc.page_content,
                            "metadata": metadata
                        })
                except Exception as e:
                    print(f"Error processing document {doc_id}: {str(e)}")
            
            return documents
        except Exception as e:
            print(f"Error getting documents: {e}")
            return []
    
    def search_documents(self, query, k=5):
        """Search for documents similar to the query."""
        try:
            docs_and_scores = self.db.similarity_search_with_score(query, k=k)
            
            results = []
            for doc, score in docs_and_scores:
                # Make sure metadata is JSON serializable
                metadata = {}
                for k, v in doc.metadata.items():
                    if isinstance(v, (str, int, float, bool, list, dict, type(None))):
                        metadata[k] = v
                    else:
                        metadata[k] = str(v)
                
                results.append({
                    "content": doc.page_content,
                    "metadata": metadata,
                    "similarity_score": float(score)
                })
            
            return results
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def get_document_by_id(self, doc_id):
        """Get a specific document by ID."""
        try:
            doc = self.db.docstore._dict.get(doc_id)
            if doc:
                # Make sure metadata is JSON serializable
                metadata = {}
                for k, v in doc.metadata.items():
                    if isinstance(v, (str, int, float, bool, list, dict, type(None))):
                        metadata[k] = v
                    else:
                        metadata[k] = str(v)
                
                return {
                    "id": str(doc_id),
                    "content": doc.page_content,
                    "metadata": metadata
                }
            return None
        except Exception as e:
            print(f"Error getting document by ID: {e}")
            return None
    
    def get_collection_statistics(self):
        """Get statistics about the vector database collection."""
        try:
            # Get all documents
            docs = list(self.db.docstore._dict.values())
            
            doc_count = len(docs)
            
            # Analyze sources
            sources = {}
            for doc in docs:
                if hasattr(doc, 'metadata'):
                    source = doc.metadata.get("source", "Unknown")
                    sources[source] = sources.get(source, 0) + 1
            
            # Calculate average document length
            total_length = sum(len(doc.page_content) for doc in docs)
            avg_length = total_length / doc_count if doc_count > 0 else 0
            
            return {
                "document_count": doc_count,
                "sources": sources,
                "average_document_length": avg_length,
                "embedding_dimensions": 384  # MiniLM embeddings size
            }
        except Exception as e:
            print(f"Error getting collection statistics: {e}")
            return {"error": str(e)}