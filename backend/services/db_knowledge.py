"""Service for answering database knowledge questions."""
from models.llm import LLMService
from services.vector_db import VectorDBService
import uuid

class DBKnowledgeService:
    """Service for answering database knowledge questions using LLM with RAG."""
    
    def __init__(self):
        """Initialize the DB Knowledge service."""
        self.llm_service = LLMService()
        self.vector_db = VectorDBService()
        self.conversation_memories = {}
        
    def clear_conversation_memory(self, conversation_id):
        """Clear conversation memory for the given ID."""
        if conversation_id in self.conversation_memories:
            del self.conversation_memories[conversation_id]
            return True
        return False
    
    def format_conversation_history(self, messages):
        """Format the conversation history into a string."""
        if not messages:
            return ""
        
        formatted_history = ""
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "user":
                formatted_history += f"Human: {content}\n"
            elif role in ["bot", "assistant"]:
                formatted_history += f"AI: {content}\n"
        
        return formatted_history
    
    def summarize_conversation(self, conversation_history, max_length=1000):
        """Summarize the conversation history if it's too long."""
        # Check if the history needs summarization
        if len(conversation_history) <= max_length:
            return conversation_history
        
        # Get the last few exchanges to preserve recent context
        last_exchanges = ""
        lines = conversation_history.strip().split('\n')
        # Keep the last 4-6 lines intact (2-3 complete exchanges)
        if len(lines) > 6:
            last_exchanges = '\n'.join(lines[-6:])
        
        # Create a summarization prompt
        prompt = f"""Summarize the following conversation between a human and an AI assistant about databases. 
Focus on key points, questions asked, and important information shared.
Keep technical database concepts, table names, and SQL syntax mentioned.

CONVERSATION:
{conversation_history[:-len(last_exchanges) if last_exchanges else None]}

Provide a concise summary that captures the essential information."""
        
        try:
            # Generate the summary
            summary = self.llm_service.generate_text(prompt, temperature=0.3)
            
            # Combine summary with recent exchanges
            if last_exchanges:
                return f"Summary of previous conversation:\n{summary}\n\nRecent exchanges:\n{last_exchanges}"
            else:
                return f"Summary of previous conversation:\n{summary}"
        except Exception as e:
            print(f"Error summarizing conversation: {e}")
            # If summarization fails, truncate the history instead
            return f"[Earlier conversation omitted for brevity]\n\n{conversation_history[-max_length:]}"
    
    def answer_question_with_context(self, conversation_id, question, messages=None, temperature=0.7):
        """Generate an answer to a database-related question with conversation context."""
        try:
            # Create new conversation ID if not provided
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            
            # Format conversation history
            conversation_history = self.format_conversation_history(messages)
            
            # Summarize the conversation history if it's too long
            if len(conversation_history) > 2000:  # Adjust threshold as needed
                conversation_history = self.summarize_conversation(conversation_history)
            
            # Retrieve relevant documents
            docs = []
            if self.vector_db.db:
                docs = self.vector_db.db.similarity_search(question, k=5)  # Reduced from 10 to 5 for efficiency
            
            # Format retrieved documents
            context = "\n\n".join([doc.page_content for doc in docs]) if docs else ""
            
            # Create appropriate prompt based on available context
            if context:
                prompt = f"""You are an expert in SQL Databases. Use the following retrieved documents and conversation history to answer the question.

Retrieved Documents:
{context}

Conversation History:
{conversation_history}

Question: {question}

Provide a clear, accurate, and helpful answer."""
            else:
                prompt = f"""You are an expert in databases and SQL. Answer the following question about databases, SQL, or data management, taking into account the conversation history.

Conversation History:
{conversation_history}

Question: {question}

Provide a clear, accurate, and helpful answer."""
            
            # Generate response using the LLM
            answer = self.llm_service.generate_text(prompt, temperature)
            
            return answer
            
        except Exception as e:
            import traceback
            print(f"Error in DB knowledge service with context: {e}")
            print(traceback.format_exc())  # Print the full traceback for debugging
            return f"Error generating an answer: {str(e)}"