"""Service pour répondre aux questions sur les bases de données."""
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
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            
            conversation_history = self.format_conversation_history(messages)
            
            if len(conversation_history) > 2000:  
                conversation_history = self.summarize_conversation(conversation_history)
            
            docs = self.vector_db.search(question, k=5)
            
            print(f"DOCUMENTS TROUVÉS: {len(docs)}")
            
            enriched_context = ""
            if docs:
                for i, doc in enumerate(docs, 1):
                    source = doc.metadata.get('source', 'Source inconnue')
                    source_name = os.path.basename(source) if isinstance(source, str) else source
                    enriched_context += f"\n--- DOCUMENT {i} (Source: {source_name}) ---\n"
                    enriched_context += doc.page_content
                    enriched_context += "\n"
            
            print("\n" + "="*50)
            print(f"QUESTION: {question}")
            print("-"*50)
            print("-"*50)
            print("CONTEXTE ENRICHI:")
            print(enriched_context if enriched_context else "AUCUN CONTEXTE TROUVÉ")
            
            if docs:
                print("-"*50)
                print("SOURCES:")
                for i, doc in enumerate(docs):
                    source = doc.metadata.get('source', 'Inconnue')
                    score = doc.metadata.get('similarity_score', 'N/A')
                    print(f"  Document {i+1}: {source} (Score: {score})")
            
            print("-"*50)
            print("HISTORIQUE DE CONVERSATION:")
            print(conversation_history if conversation_history else "AUCUN HISTORIQUE")
            print("="*50 + "\n")
            
            if enriched_context:
                prompt = f"""Tu es un expert en bases de données SQL. Utilise les documents récupérés suivants et l'historique de conversation pour répondre à la question.

    Documents Récupérés:
    {enriched_context}

    Historique de Conversation:
    {conversation_history}

    Question: {question}

    Fournis une réponse claire, précise et utile en français. Si pertinent, cite les sources des informations en te référant aux numéros des documents."""
            else:
                prompt = f"""Tu es un expert en bases de données et SQL. Réponds à la question suivante sur les bases de données, SQL ou la gestion de données, en tenant compte de l'historique de conversation.

    Historique de Conversation:
    {conversation_history}

    Question: {question}

    Fournis une réponse claire, précise et utile en français."""
            
            # Génère une réponse en utilisant le LLM
            answer = self.llm_service.generate_text(prompt, temperature)
            
            return answer
            
        except Exception as e:
            import traceback
            print(f"Erreur dans le service de connaissances DB avec contexte: {e}")
            print(traceback.format_exc())  
            return f"Erreur lors de la génération d'une réponse: {str(e)}"