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


# Create tables
Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()