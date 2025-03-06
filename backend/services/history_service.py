"""Service for managing interaction history."""
from sqlalchemy.orm import Session
from models.history import SQLHistory


class HistoryService:
    """Service for handling SQL history operations."""
    
    @staticmethod
    def add_sql_history(db: Session, description: str, dialect: str, generated_sql: str):
        """
        Add a new SQL generation entry to history.
        
        Args:
            db: Database session
            description: Natural language description
            dialect: SQL dialect used
            generated_sql: Generated SQL query
            
        Returns:
            The created history item
        """
        history_item = SQLHistory(
            description=description,
            dialect=dialect,
            generated_sql=generated_sql
        )
        
        db.add(history_item)
        db.commit()
        db.refresh(history_item)
        
        return history_item
    
    @staticmethod
    def get_sql_history(db: Session, limit: int = 50):
        """
        Get SQL generation history.
        
        Args:
            db: Database session
            limit: Maximum number of items to return
            
        Returns:
            List of history items
        """
        return db.query(SQLHistory).order_by(SQLHistory.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def get_sql_history_by_id(db: Session, history_id: int):
        """
        Get a specific SQL history item by ID.
        
        Args:
            db: Database session
            history_id: ID of the history item
            
        Returns:
            History item if found, None otherwise
        """
        return db.query(SQLHistory).filter(SQLHistory.id == history_id).first()
    
    @staticmethod
    def delete_sql_history(db: Session, history_id: int):
        """
        Delete a specific SQL history item by ID.
        
        Args:
            db: Database session
            history_id: ID of the history item to delete
            
        Returns:
            True if deleted, False if not found
        """
        history_item = db.query(SQLHistory).filter(SQLHistory.id == history_id).first()
        if history_item:
            db.delete(history_item)
            db.commit()
            return True
        return False