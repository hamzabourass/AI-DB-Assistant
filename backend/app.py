from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from services.sql_generator import SQLGeneratorService
from services.db_knowledge import DBKnowledgeService
from services.history_service import HistoryService
from services.vector_db import VectorDBService
from services.vector_db_inspector import VectorDBInspector
from services.vector_db_cleanup import VectorDBCleanupService
from services.chat_history_service import ChatHistoryService

from models.sql_request import SQLRequest
from models.knowledge_request import KnowledgeRequest
from models.history_request import HistoryDeleteRequest
from models.history import ChatHistory, get_db
from sqlalchemy.orm import Session
from models.chat_request import SaveChatRequest, GetChatRequest, DeleteChatRequest, ChatListRequest
import os
import shutil


app = FastAPI(title="AI Database Assistant API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service variables
sql_generator = None
db_knowledge_service = None
vector_db_service = None
service_initialized = False
vector_db_cleanup_service = None

# Initialize services
try:
    sql_generator = SQLGeneratorService()
    db_knowledge_service = DBKnowledgeService() 
    vector_db_service = VectorDBService()
    service_initialized = True
    print("Services initialized successfully")
    if vector_db_service:
        vector_db_cleanup_service = VectorDBCleanupService(vector_db_service)
        print("Vector DB cleanup service initialized successfully")
except Exception as e:
    print(f"Error initializing services: {e}")


@app.get("/")
def read_root():
    status = "API is running"
    if not service_initialized:
        status += " (LLM service not initialized - check API key)"
    return {"status": status}

@app.get("/api/test")
def test_endpoint():
    return {"message": "Backend connection successful"}

@app.post("/api/sql")
def generate_sql(request: SQLRequest, db: Session = Depends(get_db)):
    """Generate SQL based on natural language description."""
    if not service_initialized:
        raise HTTPException(status_code=503, detail="Services not initialized. Check API key.")
        
    if not request.description:
        raise HTTPException(status_code=400, detail="Description cannot be empty")
    
    sql = sql_generator.generate_sql(request.description, request.dialect)
    
    # Add to history
    history_item = HistoryService.add_sql_history(
        db,
        description=request.description,
        dialect=request.dialect,
        generated_sql=sql
    )
    
    return {"sql": sql, "history_id": history_item.id}

@app.get("/api/history/sql")
def get_sql_history(db: Session = Depends(get_db)):
    """Get SQL generation history."""
    history_items = HistoryService.get_sql_history(db)
    
    return {"history": [item.to_dict() for item in history_items]}


@app.get("/api/history/sql/{history_id}")
def get_sql_history_by_id(history_id: int, db: Session = Depends(get_db)):
    """Get a specific SQL history item by ID."""
    history_item = HistoryService.get_sql_history_by_id(db, history_id)
    
    if not history_item:
        raise HTTPException(status_code=404, detail="History item not found")
    
    return history_item.to_dict()


@app.delete("/api/history/sql")
def delete_sql_history(request: HistoryDeleteRequest, db: Session = Depends(get_db)):
    """Delete a specific SQL history item by ID."""
    success = HistoryService.delete_sql_history(db, request.history_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="History item not found")
    
    return {"success": True}


@app.post("/api/knowledge")
def answer_db_question(request: KnowledgeRequest):
    """Answer database-related questions."""
    import uuid  # Make sure uuid is imported here
    
    if not service_initialized:
        raise HTTPException(status_code=503, detail="Services not initialized. Check API key.")
    
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    print(f"Answering question: {request.question}")
    
    # Get conversation_id from request
    conversation_id = request.conversation_id
    
    # Get messages from request
    messages = request.messages
    
    # If conversation_id exists but no messages provided, try to get from database
    if conversation_id and not messages:
        db = next(get_db())
        try:
            chat_history = ChatHistoryService.get_chat(db, conversation_id)
            if chat_history:
                messages = chat_history.get_messages()
        except Exception as e:
            print(f"Error getting chat history: {e}")
    
    # Generate answer
    if conversation_id:
        answer = db_knowledge_service.answer_question_with_context(
            conversation_id, 
            request.question,
            messages
        )
    else:
        # Create a new conversation ID
        conversation_id = str(uuid.uuid4())
        answer = db_knowledge_service.answer_question_with_context(
            conversation_id, 
            request.question
        )
    
    print(f"Generated answer of length: {len(answer)}")
    
    return {"answer": answer, "conversation_id": conversation_id}

@app.post("/api/chat/save")
def save_chat(request: SaveChatRequest, db: Session = Depends(get_db)):
    """Save chat conversation history."""
    if not request.conversation_id:
        raise HTTPException(status_code=400, detail="Conversation ID cannot be empty")
    
    try:
        chat_history = ChatHistoryService.save_chat(
            db,
            request.conversation_id,
            request.messages,
            request.title
        )
        
        return chat_history.to_dict()
    except Exception as e:
        print(f"Error saving chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving chat: {str(e)}")

@app.get("/api/chat/{conversation_id}")
def get_chat(conversation_id: str, db: Session = Depends(get_db)):
    """Get a specific chat conversation by ID."""
    try:
        chat_history = ChatHistoryService.get_chat(db, conversation_id)
        
        if not chat_history:
            raise HTTPException(status_code=404, detail="Chat conversation not found")
        
        return chat_history.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting chat: {str(e)}")

@app.get("/api/chat/list")
def list_chats(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    """List chat conversations."""
    try:
        chat_histories = ChatHistoryService.list_chats(db, limit, offset)
        
        return {"chats": [chat.to_dict() for chat in chat_histories]}
    except Exception as e:
        print(f"Error listing chats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing chats: {str(e)}")

@app.delete("/api/chat/{conversation_id}")
def delete_chat(conversation_id: str, db: Session = Depends(get_db)):
    """Delete a specific chat conversation by ID."""
    try:
        success = ChatHistoryService.delete_chat(db, conversation_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Chat conversation not found")
        
        # Also clear the memory for this conversation
        if db_knowledge_service:
            db_knowledge_service.clear_conversation_memory(conversation_id)
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting chat: {str(e)}")

@app.post("/api/chat/new")
def create_new_chat(db: Session = Depends(get_db)):
    """Create a new empty chat conversation."""
    try:
        conversation_id = ChatHistoryService.generate_conversation_id()
        chat_history = ChatHistoryService.save_chat(
            db,
            conversation_id,
            [],
            "New Conversation"
        )
        
        return chat_history.to_dict()
    except Exception as e:
        print(f"Error creating new chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating new chat: {str(e)}")
    
@app.get("/api/chat/count")
def count_chats(db: Session = Depends(get_db)):
    """Count the number of chat conversations."""
    count = db.query(ChatHistory).count()
    return {"total_chats": count}

# Vector DB endpoints
@app.get("/api/vector-db/stats")
def get_vector_db_stats():
    """Get statistics about the vector database."""
    if not service_initialized:
        raise HTTPException(status_code=503, detail="Services not initialized. Check API key.")
    
    try:
        # Try to create VectorDBInspector
        try:
            inspector = VectorDBInspector()
            stats = inspector.get_collection_statistics()
            return stats
        except ValueError as e:
            # If the vector database doesn't exist, suggest initializing it
            return JSONResponse(
                status_code=404,
                content={
                    "error": f"Vector database not found: {str(e)}",
                    "suggestion": "Run 'python scripts/initialize_db.py' to initialize the vector database with sample data"
                }
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Error getting vector DB stats: {str(e)}",
                "traceback": str(e.__traceback__)
            }
        )

@app.get("/api/vector-db/documents")
def get_vector_db_documents(limit: int = 100, offset: int = 0):
    """Get documents from the vector database with pagination."""
    if not service_initialized:
        raise HTTPException(status_code=503, detail="Services not initialized. Check API key.")
    
    try:
        # Try to create VectorDBInspector - with debug info
        print(f"Creating VectorDBInspector...")
        
        try:
            inspector = VectorDBInspector()
            documents = inspector.get_all_documents(limit=limit, offset=offset)
            total_count = inspector.get_document_count()
            
            return {
                "documents": documents,
                "total": total_count,
                "limit": limit,
                "offset": offset
            }
        except ValueError as e:
            # Detailed error
            print(f"ValueError in get_vector_db_documents: {e}")
            return JSONResponse(
                status_code=404,
                content={
                    "error": f"Vector database not found: {str(e)}",
                    "suggestion": "Run 'python scripts/initialize_db.py' to initialize the vector database with sample data"
                }
            )
    except Exception as e:
        # Very detailed error
        import traceback
        print(f"Exception in get_vector_db_documents: {e}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Error getting vector DB documents: {str(e)}",
                "traceback": traceback.format_exc()
            }
        )

@app.get("/api/vector-db/document/{doc_id}")
def get_vector_db_document(doc_id: str):
    """Get a specific document from the vector database by ID."""
    if not service_initialized:
        raise HTTPException(status_code=503, detail="Services not initialized. Check API key.")
    
    try:
        inspector = VectorDBInspector()
        document = inspector.get_document_by_id(doc_id)
        
        if not document:
            return JSONResponse(
                status_code=404,
                content={"error": f"Document with ID {doc_id} not found"}
            )
        
        return document
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error getting document: {str(e)}"}
        )

@app.post("/api/vector-db/search")
def search_vector_db(query: str, k: int = 5):
    """Search for documents in the vector database."""
    if not service_initialized:
        raise HTTPException(status_code=503, detail="Services not initialized. Check API key.")
    
    if not query:
        return JSONResponse(
            status_code=400,
            content={"error": "Search query cannot be empty"}
        )
    
    try:
        inspector = VectorDBInspector()
        results = inspector.search_documents(query, k=k)
        
        return {"results": results}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error searching vector DB: {str(e)}"}
        )

# Cet extrait montre uniquement la fonction d'upload modifiée, à intégrer dans votre app.py


@app.post("/api/vector-db/upload")
async def upload_knowledge_document(file: UploadFile = File(...)):
    """Télécharger un document de connaissance vers la base de données vectorielle."""
    if not service_initialized:
        raise HTTPException(status_code=503, detail="Services non initialisés. Vérifiez la clé API.")
    
    try:
        # Liste des extensions autorisées
        allowed_extensions = ['.txt', '.pdf', '.docx', '.doc', '.md', '.csv', '.json', '.xml', '.html']
        
        # Vérifier l'extension du fichier
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            return JSONResponse(
                status_code=400,
                content={"error": f"Type de fichier non pris en charge. Extensions autorisées : {', '.join(allowed_extensions)}"}
            )
        
        # Créer le répertoire knowledge s'il n'existe pas
        knowledge_dir = "./knowledge"
        os.makedirs(knowledge_dir, exist_ok=True)
        
        # Enregistrer le fichier téléchargé
        file_path = os.path.join(knowledge_dir, file.filename)
        
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        print(f"Fichier sauvegardé: {file_path}")
        
        # Réindexer la base de données vectorielle
        # Option 1: Réindexation complète (plus fiable mais plus lente)
        success = vector_db_service.clear_and_reindex()
        
        # Option 2: Ajouter uniquement le nouveau document
        # success = vector_db_service.index_documents()
        
        if success:
            return {"message": f"Document {file.filename} téléchargé et indexé avec succès"}
        else:
            # Si l'indexation échoue, supprimer le fichier téléchargé
            os.remove(file_path)
            return JSONResponse(
                status_code=500,
                content={"error": "Échec de l'indexation du document"}
            )
    except Exception as e:
        import traceback
        print(f"Erreur lors du téléchargement du document : {str(e)}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": f"Erreur lors du téléchargement du document : {str(e)}"}
        )


@app.get("/api/vector-db/cleanup/files")
async def list_knowledge_files():
    """List all knowledge files that can be cleaned up."""
    if not service_initialized:
        raise HTTPException(status_code=503, detail="Services not initialized. Check API key.")
    
    if not vector_db_cleanup_service:
        raise HTTPException(status_code=503, detail="Vector DB cleanup service not initialized.")
    
    try:
        files_info = vector_db_cleanup_service.list_knowledge_files()
        return {"files": files_info}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error listing knowledge files: {str(e)}"}
        )

@app.post("/api/vector-db/cleanup/backup")
async def backup_knowledge_files():
    """Create a backup of all knowledge files."""
    if not service_initialized:
        raise HTTPException(status_code=503, detail="Services not initialized. Check API key.")
    
    if not vector_db_cleanup_service:
        raise HTTPException(status_code=503, detail="Vector DB cleanup service not initialized.")
    
    try:
        success, message = vector_db_cleanup_service.backup_knowledge_files()
        
        if success:
            return {"message": message}
        else:
            return JSONResponse(
                status_code=500,
                content={"error": message}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error backing up knowledge files: {str(e)}"}
        )

@app.delete("/api/vector-db/cleanup/file")
async def delete_knowledge_file(file_path: str):
    """Delete a specific knowledge file."""
    if not service_initialized:
        raise HTTPException(status_code=503, detail="Services not initialized. Check API key.")
    
    if not vector_db_cleanup_service:
        raise HTTPException(status_code=503, detail="Vector DB cleanup service not initialized.")
    
    try:
        success, message = vector_db_cleanup_service.delete_knowledge_file(file_path)
        
        if success:
            return {"message": message}
        else:
            return JSONResponse(
                status_code=404 if "not found" in message else 500,
                content={"error": message}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error deleting knowledge file: {str(e)}"}
        )

@app.delete("/api/vector-db/cleanup/category/{category}")
async def delete_files_by_category(category: str):
    """Delete all files of a specific category."""
    if not service_initialized:
        raise HTTPException(status_code=503, detail="Services not initialized. Check API key.")
    
    if not vector_db_cleanup_service:
        raise HTTPException(status_code=503, detail="Vector DB cleanup service not initialized.")
    
    try:
        success, message = vector_db_cleanup_service.delete_files_by_category(category)
        
        if success:
            return {"message": message}
        else:
            return JSONResponse(
                status_code=404 if "No files found" in message else 500,
                content={"error": message}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error deleting files by category: {str(e)}"}
        )

@app.post("/api/vector-db/cleanup/clear-db")
async def clear_vector_db():
    """Clear the vector database without deleting knowledge files."""
    if not service_initialized:
        raise HTTPException(status_code=503, detail="Services not initialized. Check API key.")
    
    if not vector_db_cleanup_service:
        raise HTTPException(status_code=503, detail="Vector DB cleanup service not initialized.")
    
    try:
        success, message = vector_db_cleanup_service.clear_vector_db()
        
        if success:
            return {"message": message}
        else:
            return JSONResponse(
                status_code=500,
                content={"error": message}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error clearing vector database: {str(e)}"}
        )

@app.post("/api/vector-db/cleanup/reindex")
async def reindex_knowledge():
    """Reindex all knowledge files."""
    if not service_initialized:
        raise HTTPException(status_code=503, detail="Services not initialized. Check API key.")
    
    if not vector_db_cleanup_service:
        raise HTTPException(status_code=503, detail="Vector DB cleanup service not initialized.")
    
    try:
        success, message = vector_db_cleanup_service.reindex_knowledge()
        
        if success:
            return {"message": message}
        else:
            return JSONResponse(
                status_code=500,
                content={"error": message}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error reindexing knowledge: {str(e)}"}
        )

@app.post("/api/vector-db/cleanup/clear-all")
async def clear_all_knowledge():
    """Clear all knowledge files AND the vector database."""
    if not service_initialized:
        raise HTTPException(status_code=503, detail="Services not initialized. Check API key.")
    
    if not vector_db_cleanup_service:
        raise HTTPException(status_code=503, detail="Vector DB cleanup service not initialized.")
    
    try:
        success, message = vector_db_cleanup_service.clear_all_knowledge()
        
        if success:
            return {"message": message}
        else:
            return JSONResponse(
                status_code=500,
                content={"error": message}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error clearing all knowledge: {str(e)}"}
        )