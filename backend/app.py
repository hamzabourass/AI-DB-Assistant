from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from services.sql_generator import SQLGeneratorService
from services.db_knowledge import DBKnowledgeService # New import
from services.history_service import HistoryService
from models.sql_request import SQLRequest
from models.knowledge_request import KnowledgeRequest # New import
from models.history_request import HistoryDeleteRequest
from models.history import ChatHistory, get_db
from sqlalchemy.orm import Session
from models.chat_request import SaveChatRequest, GetChatRequest, DeleteChatRequest, ChatListRequest
from services.chat_history_service import ChatHistoryService
import os


app = FastAPI(title="AI Database Assistant API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    sql_generator = SQLGeneratorService()
    db_knowledge = DBKnowledgeService() 
    service_initialized = True
except Exception as e:
    print(f"Error initializing services: {e}")
    service_initialized = False


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
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    print(f"Answering question: {request.question}")
    
    conversation_id = request.conversation_id if hasattr(request, 'conversation_id') else None
    
    if conversation_id:
        chat_history = None
        db = next(get_db())
        try:
            chat_history = ChatHistoryService.get_chat(db, conversation_id)
        except Exception as e:
            print(f"Error getting chat history: {e}")
        
        if chat_history:
            messages = chat_history.get_messages()
            answer = db_knowledge.answer_question_with_context(
                conversation_id, 
                request.question,
                messages
            )
        else:
            answer = db_knowledge.answer_question_with_context(conversation_id, request.question)
    else:
        answer = db_knowledge.answer_question(request.question)
    
    print(f"Generated answer of length: {len(answer)}")
    
    return {"answer": answer, "conversation_id": conversation_id}

# Add chat history endpoints
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
        db_knowledge.clear_conversation_memory(conversation_id)
        
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
    
@app.delete("/api/chat/{conversation_id}")
def delete_chat(conversation_id: str, db: Session = Depends(get_db)):
    """Delete a specific chat conversation by ID."""
    success = ChatHistoryService.delete_chat(db, conversation_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Chat conversation not found")
    
    return {"success": True}

# First verify if any chats exist
@app.get("/api/chat/count")
def count_chats(db: Session = Depends(get_db)):
    count = db.query(ChatHistory).count()
    return {"total_chats": count}  # If this returns 0, your database is empty