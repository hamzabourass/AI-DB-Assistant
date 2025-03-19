"""Service pour répondre aux questions sur les bases de données."""
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
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "user":
                formatted_history += f"Humain: {content}\n"
            elif role in ["bot", "assistant"]:
                formatted_history += f"IA: {content}\n"
        
        return formatted_history
    
    def summarize_conversation(self, conversation_history, max_length=1000):
        """Résume l'historique de conversation s'il est trop long."""
        if len(conversation_history) <= max_length:
            return conversation_history
        
        last_exchanges = ""
        lines = conversation_history.strip().split('\n')
        if len(lines) > 6:
            last_exchanges = '\n'.join(lines[-6:])
        
        prompt = f"""Résume la conversation suivante entre un humain et un assistant IA à propos des bases de données. 
Concentre-toi sur les points clés, les questions posées et les informations importantes partagées.
Conserve les concepts techniques de base de données, les noms de tables et la syntaxe SQL mentionnés.

CONVERSATION:
{conversation_history[:-len(last_exchanges) if last_exchanges else None]}

Fournis un résumé concis qui capture les informations essentielles."""
        
        try:
            summary = self.llm_service.generate_text(prompt, temperature=0.3)
            
            if last_exchanges:
                return f"Résumé de la conversation précédente:\n{summary}\n\nÉchanges récents:\n{last_exchanges}"
            else:
                return f"Résumé de la conversation précédente:\n{summary}"
        except Exception as e:
            print(f"Erreur lors du résumé de la conversation: {e}")
            return f"[Conversation antérieure omise par souci de concision]\n\n{conversation_history[-max_length:]}"
    

    def answer_question_with_context(self, conversation_id, question, messages=None, temperature=0.7):
        """Génère une réponse à une question sur les bases de données avec contexte de conversation."""
        try:
            # Create a debug log file that will definitely capture our output
            with open("rag_retrieval_debug.log", "a") as debug_file:
                debug_file.write(f"\n\n========================\n")
                import datetime
                debug_file.write(f"TIMESTAMP: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                debug_file.write(f"QUESTION: {question}\n")
                debug_file.write(f"CONVERSATION ID: {conversation_id}\n")
                debug_file.write(f"========================\n\n")
            
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            
            conversation_history = self.format_conversation_history(messages)
            
            if len(conversation_history) > 2000:
                conversation_history = self.summarize_conversation(conversation_history)
            
            docs = []
            if self.vector_db.db:
                # Get documents from vector DB
                docs = self.vector_db.db.similarity_search(question, k=5)
                
                # Log the retrieved documents to our debug file
                with open("rag_retrieval_debug.log", "a") as debug_file:
                    debug_file.write(f"RETRIEVED {len(docs)} DOCUMENTS:\n\n")
                    
                    for i, doc in enumerate(docs):
                        debug_file.write(f"--- DOCUMENT {i+1} ---\n")
                        debug_file.write(f"SOURCE: {doc.metadata.get('source', 'Unknown')}\n")
                        debug_file.write(f"CONTENT:\n{doc.page_content}\n\n")
            else:
                with open("rag_retrieval_debug.log", "a") as debug_file:
                    debug_file.write("NO VECTOR DB AVAILABLE\n")
            
            context = "\n\n".join([doc.page_content for doc in docs]) if docs else ""
            
            if context:
                prompt = f"""Tu es un expert en bases de données SQL. Utilise les documents récupérés suivants et l'historique de conversation pour répondre à la question.

    Documents Récupérés:
    {context}

    Historique de Conversation:
    {conversation_history}

    Question: {question}

    Fournis une réponse claire, précise et utile en français."""
            else:
                prompt = f"""Tu es un expert en bases de données et SQL. Réponds à la question suivante sur les bases de données, SQL ou la gestion de données, en tenant compte de l'historique de conversation.

    Historique de Conversation:
    {conversation_history}

    Question: {question}

    Fournis une réponse claire, précise et utile en français."""
            
            # Génère une réponse en utilisant le LLM
            answer = self.llm_service.generate_text(prompt, temperature)
            
            # Log the answer too
            with open("rag_retrieval_debug.log", "a") as debug_file:
                debug_file.write(f"ANSWER:\n{answer[:200]}...\n\n")
            
            return answer
            
        except Exception as e:
            import traceback
            error_msg = f"Erreur dans le service de connaissances DB: {e}\n{traceback.format_exc()}"
            
            # Log the error to our debug file
            with open("rag_retrieval_debug.log", "a") as debug_file:
                debug_file.write(f"ERROR:\n{error_msg}\n\n")
                
            return f"Erreur lors de la génération d'une réponse: {str(e)}"