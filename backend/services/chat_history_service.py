# In services/chat_history_service.py:

"""Service for managing chat conversation history."""
from typing import List, Optional
from sqlalchemy.orm import Session
from models.history import ChatHistory  # Import from history, not chat_history
import json
import uuid

class ChatHistoryService:
    """Service for handling chat history operations."""
    
    @staticmethod
    def generate_conversation_id() -> str:
        """Generate a unique conversation ID."""
        return str(uuid.uuid4())
    
    @staticmethod
    def save_chat(db: Session, conversation_id: str, messages, title=None):
        """Save or update a chat conversation."""
        # Check if conversation exists
        chat_history = db.query(ChatHistory).filter(
            ChatHistory.conversation_id == conversation_id
        ).first()
        
        if chat_history:
            # Update existing conversation
            chat_history.set_messages(messages)
            if title:
                chat_history.title = title
        else:
            # Create new conversation
            chat_history = ChatHistory(
                conversation_id=conversation_id,
                title=title or f"Conversation {conversation_id[:8]}"
            )
            chat_history.set_messages(messages)
            db.add(chat_history)
        
        db.commit()
        db.refresh(chat_history)
        
        return chat_history
    
    @staticmethod
    def get_chat(db: Session, conversation_id: str) -> Optional[ChatHistory]:
        """
        Get a chat conversation by ID.
        
        Args:
            db: Database session
            conversation_id: Unique identifier for the conversation
            
        Returns:
            The chat history item if found, None otherwise
        """
        return db.query(ChatHistory).filter(
            ChatHistory.conversation_id == conversation_id
        ).first()
    
    @staticmethod
    def list_chats(db: Session, limit: int = 20, offset: int = 0) -> List[ChatHistory]:
        """
        List chat conversations, ordered by most recent.
        
        Args:
            db: Database session
            limit: Maximum number of conversations to return
            offset: Pagination offset
            
        Returns:
            List of chat history items
        """
        return db.query(ChatHistory).order_by(
            ChatHistory.updated_at.desc()
        ).offset(offset).limit(limit).all()
    
    @staticmethod
    def delete_chat(db: Session, conversation_id: str) -> bool:
        """
        Delete a chat conversation.
        
        Args:
            db: Database session
            conversation_id: Unique identifier for the conversation
            
        Returns:
            True if deleted, False if not found
        """
        chat_history = db.query(ChatHistory).filter(
            ChatHistory.conversation_id == conversation_id
        ).first()
        
        if chat_history:
            db.delete(chat_history)
            db.commit()
            return True
        
        return False