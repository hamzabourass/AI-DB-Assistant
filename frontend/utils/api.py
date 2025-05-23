import requests

API_URL = "http://localhost:8000" 

def check_api_status():
    """Check if the backend API is available."""
    try:
        response = requests.get(f"{API_URL}/api/test", timeout=None)
        if response.status_code == 200:
            return {"connected": True, "status_code": response.status_code}
        else:
            return {"connected": False, "status_code": response.status_code}
    except requests.exceptions.ConnectionError:
        return {"connected": False, "status_code": None, "error": "Connection refused"}
    except requests.exceptions.Timeout:
        return {"connected": False, "status_code": None, "error": "Connection timeout"}
    except Exception as e:
        return {"connected": False, "status_code": None, "error": str(e)}


def answer_db_question(question, conversation_id=None, messages=None):
    """Get answer to a database-related question with optional conversation context."""
    try:
        payload = {"question": question}
        
        # Add conversation_id to payload if provided
        if conversation_id:
            payload["conversation_id"] = conversation_id
            
        # Add messages to payload if provided
        if messages:
            payload["messages"] = messages
            
        response = requests.post(
            f"{API_URL}/api/knowledge",
            json=payload,

            
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "answer": data["answer"],
                "conversation_id": data.get("conversation_id")
            }
        else:
            return {
                "success": False,
                "error": f"Error: {response.status_code}",
                "message": response.text if response.text else "Unknown error"
            }
    except Exception as e:
        return {
            "success": False,
            "error": "Connection error",
            "message": str(e)
        }

def save_chat(conversation_id, messages, title=None):
    """Save a chat conversation to the backend."""
    try:
        response = requests.post(
            f"{API_URL}/api/chat/save",
            json={
                "conversation_id": conversation_id,
                "messages": messages,
                "title": title
            },
            timeout=None
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "chat": response.json()
            }
        else:
            return {
                "success": False,
                "error": f"Error: {response.status_code}",
                "message": response.text if response.text else "Unknown error"
            }
    except Exception as e:
        return {
            "success": False,
            "error": "Connection error",
            "message": str(e)
        }

def get_chat(conversation_id):
    """Get a chat conversation from the backend."""
    try:
        response = requests.get(
            f"{API_URL}/api/chat/{conversation_id}",
            timeout=None
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "chat": response.json()
            }
        else:
            return {
                "success": False,
                "error": f"Error: {response.status_code}",
                "message": response.text if response.text else "Unknown error"
            }
    except Exception as e:
        return {
            "success": False,
            "error": "Connection error",
            "message": str(e)
        }

def create_new_chat():
    """Create a new chat conversation on the backend."""
    try:
        response = requests.post(
            f"{API_URL}/api/chat/new",
            timeout=None
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "chat": response.json()
            }
        else:
            return {
                "success": False,
                "error": f"Error: {response.status_code}",
                "message": response.text if response.text else "Unknown error"
            }
    except Exception as e:
        return {
            "success": False,
            "error": "Connection error",
            "message": str(e)
        }

# Vector DB API functions
def get_vector_db_stats():
    """Get statistics about the vector database."""
    try:
        response = requests.get(f"{API_URL}/api/vector-db/stats", timeout=None)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Error: {response.status_code}",
                "message": response.text if response.text else "Unknown error"
            }
    except Exception as e:
        return {
            "error": "Connection error",
            "message": str(e)
        }

def get_vector_db_documents(limit=100, offset=0):
    """Get documents from the vector database with pagination."""
    try:
        response = requests.get(
            f"{API_URL}/api/vector-db/documents?limit={limit}&offset={offset}",
            timeout=None
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Error: {response.status_code}",
                "message": response.text if response.text else "Unknown error"
            }
    except Exception as e:
        return {
            "error": "Connection error",
            "message": str(e)
        }

def get_vector_db_document(doc_id):
    """Get a specific document from the vector database by ID."""
    try:
        response = requests.get(
            f"{API_URL}/api/vector-db/document/{doc_id}",
            timeout=None
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Error: {response.status_code}",
                "message": response.text if response.text else "Unknown error"
            }
    except Exception as e:
        return {
            "error": "Connection error",
            "message": str(e)
        }

def search_vector_db(query, k=5):
    """Search for documents in the vector database."""
    try:
        response = requests.post(
            f"{API_URL}/api/vector-db/search",
            params={"query": query, "k": k},
            timeout=None
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Error: {response.status_code}",
                "message": response.text if response.text else "Unknown error"
            }
    except Exception as e:
        return {
            "error": "Connection error",
            "message": str(e)
        }

def upload_knowledge_document(file):
    """Télécharger un document de connaissance vers la base de données vectorielle."""
    try:
        # Déterminer le type MIME à partir du type de fichier
        mime_type = "text/plain"  # Par défaut
        
        if file.name.endswith('.pdf'):
            mime_type = "application/pdf"
        elif file.name.endswith('.docx'):
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif file.name.endswith('.csv'):
            mime_type = "text/csv"
        elif file.name.endswith('.md'):
            mime_type = "text/markdown"
        elif file.name.endswith('.html'):
            mime_type = "text/html"
        elif file.name.endswith('.xml'):
            mime_type = "application/xml"
        elif file.name.endswith('.json'):
            mime_type = "application/json"
        
        # Créer un objet fichier à partir du fichier téléchargé
        files = {"file": (file.name, file, mime_type)}
        
        response = requests.post(
            f"{API_URL}/api/vector-db/upload",
            files=files,
            timeout=None  # Timeout plus long pour les téléchargements
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Erreur: {response.status_code}",
                "message": response.text if response.text else "Erreur inconnue"
            }
    except Exception as e:
        return {
            "error": "Erreur de connexion",
            "message": str(e)
        }

def list_knowledge_files():
    """Get a list of all knowledge files."""
    try:
        response = requests.get(
            f"{API_URL}/api/vector-db/cleanup/files",
            timeout=None
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Error: {response.status_code}",
                "message": response.text if response.text else "Unknown error"
            }
    except Exception as e:
        return {
            "error": "Connection error",
            "message": str(e)
        }

def backup_knowledge_files():
    """Create a backup of all knowledge files."""
    try:
        response = requests.post(
            f"{API_URL}/api/vector-db/cleanup/backup",
            timeout=None  # Longer timeout for backup
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Error: {response.status_code}",
                "message": response.text if response.text else "Unknown error"
            }
    except Exception as e:
        return {
            "error": "Connection error",
            "message": str(e)
        }

def delete_knowledge_file(file_path):
    """Delete a specific knowledge file."""
    try:
        response = requests.delete(
            f"{API_URL}/api/vector-db/cleanup/file",
            params={"file_path": file_path},
            timeout=None
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Error: {response.status_code}",
                "message": response.text if response.text else "Unknown error"
            }
    except Exception as e:
        return {
            "error": "Connection error",
            "message": str(e)
        }

def delete_files_by_category(category):
    """Delete all files of a specific category."""
    try:
        response = requests.delete(
            f"{API_URL}/api/vector-db/cleanup/category/{category}",
            timeout=None
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Error: {response.status_code}",
                "message": response.text if response.text else "Unknown error"
            }
    except Exception as e:
        return {
            "error": "Connection error",
            "message": str(e)
        }

def clear_vector_db():
    """Clear the vector database without deleting knowledge files."""
    try:
        response = requests.post(
            f"{API_URL}/api/vector-db/cleanup/clear-db",
            timeout=None
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Error: {response.status_code}",
                "message": response.text if response.text else "Unknown error"
            }
    except Exception as e:
        return {
            "error": "Connection error",
            "message": str(e)
        }

def reindex_knowledge():
    """Reindex all knowledge files."""
    try:
        response = requests.post(
            f"{API_URL}/api/vector-db/cleanup/reindex",
            timeout=None # Longer timeout for reindexing
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Error: {response.status_code}",
                "message": response.text if response.text else "Unknown error"
            }
    except Exception as e:
        return {
            "error": "Connection error",
            "message": str(e)
        }

def clear_all_knowledge():
    """Clear all knowledge files AND the vector database."""
    try:
        response = requests.post(
            f"{API_URL}/api/vector-db/cleanup/clear-all",
            timeout=None  # Longer timeout for complete cleanup
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Error: {response.status_code}",
                "message": response.text if response.text else "Unknown error"
            }
    except Exception as e:
        return {
            "error": "Connection error",
            "message": str(e)
        }


def upload_video_for_transcription(file, model_size="base"):
    """Upload a video file for transcription and indexing."""
    try:
        # Create a FormData-like structure
        files = {"file": (file.name, file, file.type)}
        
        # Add model_size as a form field
        data = {"model_size": model_size}
        
        response = requests.post(
            f"{API_URL}/api/video-transcription/upload",
            files=files,
            data=data,
            timeout=None  # Longer timeout for video processing
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Error: {response.status_code}",
                "message": response.text if response.text else "Unknown error"
            }
    except Exception as e:
        return {
            "error": "Connection error",
            "message": str(e)
        }

def list_transcriptions():
    """Get list of available video transcriptions."""
    try:
        response = requests.get(
            f"{API_URL}/api/video-transcription/list",
            timeout=None
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Error: {response.status_code}",
                "message": response.text if response.text else "Unknown error"
            }
    except Exception as e:
        return {
            "error": "Connection error",
            "message": str(e)
        }

def get_transcription(transcription_id):
    """Get a specific transcription by ID."""
    try:
        response = requests.get(
            f"{API_URL}/api/video-transcription/{transcription_id}",
            timeout=None
            
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Error: {response.status_code}",
                "message": response.text if response.text else "Unknown error"
            }
    except Exception as e:
        return {
            "error": "Connection error",
            "message": str(e)
        }