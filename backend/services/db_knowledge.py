"""Service pour répondre aux questions sur les bases de données."""
import os
import os
from models.llm import LLMService
from services.vector_db import VectorDBService
import uuid

class DBKnowledgeService:
    """Service pour répondre aux questions sur les bases de données en utilisant un LLM avec RAG."""
    
    def __init__(self):
        """Initialise le service de connaissances DB."""
        self.llm_service = LLMService()
        self.vector_db = VectorDBService()
        self.conversation_memories = {}
        
    def clear_conversation_memory(self, conversation_id):
        """Efface la mémoire de conversation pour l'ID donné."""
        if conversation_id in self.conversation_memories:
            del self.conversation_memories[conversation_id]
            return True
        return False
    
    def format_conversation_history(self, messages):
        """Formate l'historique de conversation en une chaîne de caractères."""
        if not messages:
            return ""
        
        formatted_history = ""
        # For local models, keep only last 4-6 exchanges to save context
        recent_messages = messages[-6:] if len(messages) > 6 else messages
        
        for msg in recent_messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "user":
                formatted_history += f"Humain: {content}\n"
            elif role in ["bot", "assistant"]:
                # Truncate long responses for context
                if len(content) > 500:
                    content = content[:500] + "..."
                formatted_history += f"IA: {content}\n"
        
        return formatted_history
    
    def summarize_conversation(self, conversation_history, max_length=800):
        """Résume l'historique de conversation s'il est trop long."""
        if len(conversation_history) <= max_length:
            return conversation_history
        
        # For local models, use a simpler approach
        lines = conversation_history.strip().split('\n')
        
        # Keep only the most recent exchanges
        if len(lines) > 4:
            return '\n'.join(lines[-4:])
        
        return conversation_history[-max_length:]
    
    def answer_question_with_context(self, conversation_id, question, messages=None, temperature=0.7):
        """Génère une réponse à une question sur les bases de données avec contexte de conversation."""
        try:
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            
            conversation_history = self.format_conversation_history(messages)
            
            # Reduced context for local models
            if len(conversation_history) > 800:  
                conversation_history = self.summarize_conversation(conversation_history)
            
            # Reduce number of retrieved docs for local models
            docs = self.vector_db.search(question, k=3)  # Reduced from 5 to 3
            
            print(f"DOCUMENTS TROUVÉS: {len(docs)}")
            
            enriched_context = ""
            source_files = []  # Track source files
            
            if docs:
                for i, doc in enumerate(docs, 1):
                    source = doc.metadata.get('source', 'Source inconnue')
                    source_name = os.path.basename(source) if isinstance(source, str) else source
                    source_files.append(source_name)
                    
                    # Limit document content for local models
                    content = doc.page_content
                    if len(content) > 400:  # Truncate long documents
                        content = content[:400] + "..."
                    
                    enriched_context += f"\n--- {source_name} ---\n"
                    enriched_context += content
                    enriched_context += "\n"
            
            # Simplified prompt for local models
            if enriched_context:
                # Include source files in prompt for the model to reference
                prompt = f"""Tu es un assistant. Détaile ta réponse en utilisant les documents suivants et si les documents fournis ne sont pas utiles pour répondre à la question, ne les mentionne pas.

Documents disponibles:
{enriched_context}
- Si tu utilises des informations des documents, mentionnes en bold

Conversation:
{conversation_history}

    Question: {question}

Instructions:
- Réponds en français
- Si tu utilises des informations des documents, mentionne le nom du fichier source en bold
- Si les documents fournis ne sont pas utiles pour répondre à la question, ne les mentionne pas
- Réponds naturellement

Réponse:"""
            else:
                # No documents found - use only model's knowledge
                prompt = f"""Tu es un assistant. Réponds de manière concise et précise.

Conversation:
{conversation_history}

    Question: {question}

Réponds en français en utilisant tes connaissances générales sur les bases de données SQL:"""
            
            # Generate response with lower temperature for consistency
            answer = self.llm_service.generate_text(prompt, temperature=0.5)
            
            return answer
            
        except Exception as e:
            import traceback
            print(f"Erreur dans le service de connaissances DB avec contexte: {e}")
            print(traceback.format_exc())  
            print(traceback.format_exc())  
            return f"Erreur lors de la génération d'une réponse: {str(e)}"