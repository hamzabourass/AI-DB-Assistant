import requests

API_URL = "http://localhost:8000" 

def check_api_status():
    """Check if the backend API is available."""
    try:
        response = requests.get(f"{API_URL}/api/test", timeout=3)
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

def generate_sql(description, dialect):
    """Generate SQL query from natural language description."""
    try:
        response = requests.post(
            f"{API_URL}/api/sql",
            json={"description": description, "dialect": dialect},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "sql": data["sql"],
                "history_id": data.get("history_id")
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

def get_sql_history():
    """Get SQL generation history."""
    try:
        response = requests.get(f"{API_URL}/api/history/sql", timeout=10)
        
        if response.status_code == 200:
            return {
                "success": True,
                "history": response.json()["history"]
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

def get_sql_history_by_id(history_id):
    """Get a specific SQL history item by ID."""
    try:
        response = requests.get(f"{API_URL}/api/history/sql/{history_id}", timeout=10)
        
        if response.status_code == 200:
            return {
                "success": True,
                "history_item": response.json()
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

def delete_sql_history(history_id):
    """Delete a specific SQL history item by ID."""
    try:
        response = requests.delete(
            f"{API_URL}/api/history/sql",
            json={"history_id": history_id},
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                "success": True
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

def answer_db_question(question, conversation_id=None):
    """Get answer to a database-related question with optional conversation context."""
    try:
        payload = {"question": question}
        
        # Add conversation_id to payload if provided
        if conversation_id:
            payload["conversation_id"] = conversation_id
            
        response = requests.post(
            f"{API_URL}/api/knowledge",
            json=payload,
            timeout=15  # Longer timeout for knowledge answers
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
            timeout=5
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
            timeout=5
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

def list_chats(limit=20, offset=0):
    """List chat conversations from the backend."""
    try:
        response = requests.get(
            f"{API_URL}/api/chat/list?limit={limit}&offset={offset}",
            timeout=5
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "chats": response.json()["chats"]
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

def delete_chat(conversation_id):
    """Delete a chat conversation from the backend."""
    try:
        response = requests.delete(
            f"{API_URL}/api/chat/{conversation_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            return {
                "success": True
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
            timeout=5
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
        response = requests.get(f"{API_URL}/api/vector-db/stats", timeout=10)
        
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
            timeout=10
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
            timeout=10
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
            timeout=10
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
    """Upload a knowledge document to the vector database."""
    try:
        # Create a file object from the uploaded file
        files = {"file": (file.name, file, "text/plain")}
        
        response = requests.post(
            f"{API_URL}/api/vector-db/upload",
            files=files,
            timeout=30  # Longer timeout for uploads
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