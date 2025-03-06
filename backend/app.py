from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.sql_generator import SQLGeneratorService
from models.sql_request import SQLRequest
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