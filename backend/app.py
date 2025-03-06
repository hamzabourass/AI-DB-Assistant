from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from services.sql_generator import SQLGeneratorService
from services.history_service import HistoryService
from models.sql_request import SQLRequest
from models.history_request import HistoryDeleteRequest
from models.history import get_db
from sqlalchemy.orm import Session
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
def generate_sql(request: SQLRequest):
    """Generate SQL based on natural language description."""
    if not request.description:
        raise HTTPException(status_code=400, detail="Description cannot be empty")
    
    sql = sql_generator.generate_sql(request.description, request.dialect)
    return {"sql": sql}

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