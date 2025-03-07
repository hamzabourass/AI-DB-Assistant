"""Database models for storing interaction history."""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
import os

# Create database directory if it doesn't exist
os.makedirs("./database", exist_ok=True)

# Initialize SQLAlchemy
Base = declarative_base()
engine = create_engine("sqlite:///database/history.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class SQLHistory(Base):
    """Model for storing SQL generation history."""
    
    __tablename__ = "sql_history"
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    dialect = Column(String(50), nullable=False)
    generated_sql = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "dialect": self.dialect,
            "generated_sql": self.generated_sql,
            "timestamp": self.timestamp.isoformat()
        }


class ChatHistory(Base):
    """Model for storing chat conversation history."""
    
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(50), nullable=False, index=True)
    messages = Column(Text, nullable=False)  # Store JSON as text
    title = Column(String(200), nullable=True)  # Optional conversation title
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "messages": self.messages,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def get_messages(self):
        """Convert stored JSON string to messages list."""
        if self.messages:
            import json
            return json.loads(self.messages)
        return []
    
    # In ChatHistory model, modify set_messages:
    def set_messages(self, messages_list):
        import json
        # Add validation
        if not isinstance(messages_list, list):
            raise ValueError("Messages must be a list")
        # Ensure proper serialization
        self.messages = json.dumps(messages_list, ensure_ascii=False)

        
# Create tables
Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()