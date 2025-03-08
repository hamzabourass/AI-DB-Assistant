"""Service for answering database knowledge questions."""
from models.llm import LLMService
from services.vector_db import VectorDBService
import uuid
import json

class DBKnowledgeService:
    """Service for answering database knowledge questions using LLM with RAG."""
    
    def __init__(self):
        """Initialize the DB Knowledge service."""
        self.llm_service = LLMService()
        self.vector_db = VectorDBService()
        self.conversation_memories = {}
        
        # Prompt templates
        self.rag_prompt_template = """You are an expert in Oracle Database. Use the following retrieved documents and conversation history to answer the question.

Retrieved Documents:
{context}

Conversation History:
{history}

Question: {question}

Provide a clear, accurate, and helpful answer. Include examples where appropriate to illustrate concepts. If the retrieved documents include database schema information, use it to provide specific, contextually relevant examples in your answer. If you're unsure about any part of your answer, acknowledge the uncertainty rather than providing potentially incorrect information."""
        
        self.no_rag_prompt_template = """You are an expert in databases and SQL. Answer the following question about databases, SQL, or data management:

Question: {question}

Provide a clear, accurate, and helpful answer. Include examples where appropriate to illustrate concepts. If you're unsure about any part of your answer, acknowledge the uncertainty rather than providing potentially incorrect information."""
        
        self.conversation_prompt_template = """You are an expert in databases and SQL. Answer the following question about databases, SQL, or data management, taking into account the conversation history.

Conversation History:
{history}

Question: {question}

Provide a clear, accurate, and helpful answer. Include examples where appropriate to illustrate concepts. If you're unsure about any part of your answer, acknowledge the uncertainty rather than providing potentially incorrect information."""
        
        # Schema-specific prompt template
        self.schema_prompt_template = """You are an expert in databases and SQL. The user has asked a question related to database schemas or structure. Use the following retrieved schema information and conversation history to provide a detailed answer.

Retrieved Schema Information:
{context}

Conversation History:
{history}

Question: {question}

When answering:
1. If the question is about a specific table or column, provide details from the retrieved schema.
2. If the question is about relationships between tables, explain the foreign key relationships.
3. If the question is about writing a query, use the exact table and column names from the schema.
4. Include relevant SQL examples that would work with the described schema.
5. Explain any potential optimizations related to the schema (indexes, normalization, etc.)

Provide a clear, accurate, and helpful answer that directly addresses the user's question about the database schema."""
    
    def get_conversation_memory(self, conversation_id):
        """Get or create conversation memory for the given ID."""
        if conversation_id not in self.conversation_memories:
            self.conversation_memories[conversation_id] = []
        return self.conversation_memories[conversation_id]
    
    def clear_conversation_memory(self, conversation_id):
        """Clear conversation memory for the given ID."""
        if conversation_id in self.conversation_memories:
            del self.conversation_memories[conversation_id]
            return True
        return False
    
    def format_chat_history(self, messages):
        """Format chat history for inclusion in prompt."""
        if not messages:
            return ""
        
        formatted_history = ""
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "user":
                formatted_history += f"Human: {content}\n"
            elif role == "bot":
                formatted_history += f"AI: {content}\n"
        
        return formatted_history.strip()
    
    def is_schema_related_question(self, question):
        """Determine if a question is related to database schema."""
        # Keywords that suggest a schema-related question
        schema_keywords = [
            "schema", "table", "column", "field", "primary key", "foreign key",
            "relationship", "entity", "attribute", "database design", "data model",
            "structure", "database structure", "ER diagram", "entity relationship",
            "data type", "constraint", "index", "normalized", "normalization"
        ]
        
        question_lower = question.lower()
        
        # Check for schema keywords
        for keyword in schema_keywords:
            if keyword in question_lower:
                return True
        
        return False
    
    def answer_question(self, question, temperature=0.7):
        """Generate an answer to a database-related question without context."""
        try:
            # Generate a new conversation ID
            conversation_id = str(uuid.uuid4())
            
            # Check if this is a schema-related question
            is_schema_question = self.is_schema_related_question(question)
            
            # Try to retrieve relevant documents from vector DB
            docs = self.vector_db.search(question, k=10 if is_schema_question else 4)
            
            if docs:
                # Format retrieved documents
                context = "\n\n".join([doc.page_content for doc in docs])
                
                # Use schema-specific prompt for schema questions
                if is_schema_question:
                    prompt = self.schema_prompt_template.format(
                        context=context,
                        history="",
                        question=question
                    )
                else:
                    # Use RAG prompt
                    prompt = self.rag_prompt_template.format(
                        context=context,
                        history="",
                        question=question
                    )
            else:
                # Use standard prompt if no relevant documents found
                prompt = self.no_rag_prompt_template.format(question=question)
            
            # Generate answer
            answer = self.llm_service.generate_text(prompt, temperature=temperature)
            
            # Initialize conversation memory
            self.conversation_memories[conversation_id] = [
                {"role": "user", "content": question},
                {"role": "bot", "content": answer}
            ]
            
            return answer
        except Exception as e:
            print(f"Error in DB knowledge service: {e}")
            return f"Error generating an answer: {str(e)}"
    
    def answer_question_with_context(self, conversation_id, question, messages=None, temperature=0.7):
        """Generate an answer to a database-related question with conversation context."""
        try:
            # Create new conversation ID if not provided
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            
            # Initialize conversation memory if needed
            if conversation_id not in self.conversation_memories:
                self.conversation_memories[conversation_id] = []
                
                # If messages provided, use them to initialize memory
                if messages:
                    self.conversation_memories[conversation_id] = messages.copy()
            
            # Format conversation history
            conversation_history = ""
            if messages:
                conversation_history = self.format_chat_history(messages)
            elif self.conversation_memories[conversation_id]:
                conversation_history = self.format_chat_history(self.conversation_memories[conversation_id])
            
            # Check if this is a schema-related question
            is_schema_question = self.is_schema_related_question(question)
            
            # Try to retrieve relevant documents from vector DB
            docs = self.vector_db.search(question, k=5 if is_schema_question else 4)
            
            if docs:
                # Format retrieved documents
                context = "\n\n".join([doc.page_content for doc in docs])
                
                # Use schema-specific prompt for schema questions
                if is_schema_question:
                    prompt = self.schema_prompt_template.format(
                        context=context,
                        history=conversation_history,
                        question=question
                    )
                else:
                    # Use RAG prompt with conversation history
                    prompt = self.rag_prompt_template.format(
                        context=context,
                        history=conversation_history,
                        question=question
                    )
            else:
                # Use conversation prompt if no relevant documents found
                prompt = self.conversation_prompt_template.format(
                    history=conversation_history,
                    question=question
                )
            
            # Generate answer
            answer = self.llm_service.generate_text(prompt, temperature=temperature)
            
            # Update conversation memory
            self.conversation_memories[conversation_id].append({"role": "user", "content": question})
            self.conversation_memories[conversation_id].append({"role": "bot", "content": answer})
            
            return answer
        except Exception as e:
            print(f"Error in DB knowledge service with context: {e}")
            return f"Error generating an answer: {str(e)}"