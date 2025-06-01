"""Service pour répondre aux questions sur les bases de données avec RAG amélioré et intégration de données de schéma."""
import os
from models.llm import LLMService
from services.vector_db import VectorDBService
from services.schema_metadata_service import SchemaMetadataService
from services.query_classifier_service import QueryClassifierService
import uuid
import json

class DBKnowledgeService:
    """Service pour répondre aux questions sur les bases de données en utilisant un LLM avec RAG amélioré."""
    
    def __init__(self):
        """Initialise le service de connaissances DB amélioré."""
        self.llm_service = LLMService()
        self.vector_db = VectorDBService()
        self.schema_metadata_service = SchemaMetadataService()
        self.query_classifier = QueryClassifierService(self.llm_service)
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
    
    def _organize_schema_data(self, schema_data, schema_type_detection):
        """
        Organizes raw schema data from Oracle APEX Cloud REST API into a structured, 
        readable format using an LLM service.
        
        Args:
            schema_data (str): Raw JSON text containing schema information (tables, indexes, views, etc.)
            
        Returns:
            str: Structured and formatted schema information ready for human consumption or further LLM processing
        """
    
        
        try:
            # First determine what we're working with
            schema_type = self.llm_service.generate_text(schema_type_detection, temperature=0.1)
            
            # Now create a specific prompt based on the schema type
            prompt = f"""
            I need you to organize and format the following raw Oracle database schema information
            into a clear, structured format that's easy to understand. The data appears to represent
            {schema_type}.
            
            Here's the raw data:
            {schema_data}
            
            Please organize this data using the following guidelines:
            
            1. If these are tables:
            - Group by table name
            - For each table, list columns with their data types, constraints, and descriptions
            - Note primary keys, foreign keys, and indexes
            - Include any additional metadata that would be helpful
            
            2. If these are views:
            - List each view name
            - Provide the view definition/query
            - List the columns returned by the view
            - Note any dependencies
            
            3. If these are indexes:
            - Group by table name
            - For each index, show type (B-tree, bitmap, etc.), columns indexed, uniqueness
            - Note if it's a primary key index
            
            4. For any other object type:
            - Organize in a logical hierarchy
            - Highlight key properties and relationships
            
            Format the output in a clean, readable structure with clear headings and sections.
            Use markdown formatting for better readability.
            """
            
            structured_data = self.llm_service.generate_text(prompt, temperature=0.3)
            return structured_data
        except Exception as e:
            print(f"Erreur lors de l'organisation des données de schéma: {e}")
            # Return a more informative error message
            return f"Impossible d'organiser les données du schéma en raison d'une erreur: {str(e)}"
            
    
    def _fetch_schema_data(self, query_info):
        """Fetch schema data based on query classification.
        
        Args:
            query_info: Dictionary with classification information
            
        Returns:
            Dictionary with schema data for each requested type
        """
        schema_data = {}
        
        try:
            if query_info['classification'] == 'multi':
                # Handle multi-type queries
                for schema_type in query_info['sub_types']:
                    if schema_type == 'tables':
                        schema_data['tables'] = self.schema_metadata_service.fetch_tables()
                    elif schema_type == 'views':
                        schema_data['views'] = self.schema_metadata_service.fetch_views()
                    elif schema_type == 'indexes':
                        schema_data['indexes'] = self.schema_metadata_service.fetch_indexes()
                    elif schema_type == 'foreign_keys':
                        schema_data['foreign_keys'] = self.schema_metadata_service.fetch_foreign_keys()
            else:
                # Handle single-type queries
                schema_type = query_info['classification']
                if schema_type == 'tables':
                    schema_data['tables'] = self.schema_metadata_service.fetch_tables()
                elif schema_type == 'views':
                    schema_data['views'] = self.schema_metadata_service.fetch_views()
                elif schema_type == 'indexes':
                    schema_data['indexes'] = self.schema_metadata_service.fetch_indexes()
                elif schema_type == 'foreign_keys':
                    schema_data['foreign_keys'] = self.schema_metadata_service.fetch_foreign_keys()
        
        except Exception as e:
            print(f"Error fetching schema data: {e}")
        
        return schema_data
    
    def _generate_schema_response(self, query, schema_data,classification, conversation_history=""):
        """Generate a markdown response based on schema data.
        
        Args:
            query: The user's query
            schema_data: Dictionary with schema data
            conversation_history: Formatted conversation history
            
        Returns:
            Generated response from LLM
        """
        # Format schema data for the LLM
        formatted_schema = self._organize_schema_data(schema_data, classification)
        # Create prompt for LLM
        prompt = f"""Tu es un expert en bases de données SQL qui aide à comprendre le schéma de base de données.
L'utilisateur a posé la question suivante sur le schéma de la base de données:

If Question is not about the schema or without any context, just answer the question.
Else :
Question: {query} 

Voici les informations du schéma:
{formatted_schema}

Historique de Conversation:
{conversation_history}

Utilise ces informations pour répondre de manière claire, précise et utile à la question de l'utilisateur.
Présente les informations du schéma de manière structurée et lisible.
Si pertinent, mentionne les relations entre les tables ou d'autres éléments de schéma.
N'invente pas d'informations qui ne sont pas présentes dans les données fournies.
"""
        
        try:
            return self.llm_service.generate_text(prompt, temperature=0.3)
        except Exception as e:
            return f"Désolé, je n'ai pas pu traiter les informations du schéma pour répondre à votre question. Erreur: {str(e)}"
    
    def answer_question_with_context(self, conversation_id, question, messages=None, temperature=0.7):
        """Génère une réponse à une question sur les bases de données avec contexte de conversation."""
        try:
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            
            conversation_history = self.format_conversation_history(messages)
            
            if len(conversation_history) > 2000:  
                conversation_history = self.summarize_conversation(conversation_history)
            
            # Classify the query to determine data source
            query_info = self.query_classifier.get_multi_type_query_info(question)
            print(f"Query classified as: {json.dumps(query_info)}")
            
            # If this is a schema-related query, use the schema metadata service
            if query_info['is_schema_query']:
                # Fetch schema data
                schema_data = self._fetch_schema_data(query_info)
                
                # Generate response based on schema data
                if schema_data:
                    response = self._generate_schema_response(question, schema_data,query_info['classification'], conversation_history)
                    return response
                else:
                    # Fallback to vector DB if schema data retrieval failed
                    print("Schema data retrieval failed, falling back to vector DB")
            
            # For general knowledge questions, use the vector database
            docs = self.vector_db.search(question, k=5)
            
            print(f"DOCUMENTS TROUVÉS: {len(docs)}")
            
            enriched_context = ""
            if docs:
                for i, doc in enumerate(docs, 1):
                    source = doc.metadata.get('source', 'Source inconnue')
                    source_name = os.path.basename(source) if isinstance(source, str) else source
                    enriched_context += f"\n---  (Source: {source_name}) ---\n"
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

        Fournis une réponse claire, précise et utile en français. et si la question etais une salutation repond normalement. Si pertinent, cite les sources des informations en te référant aux numéros des documents."""
            
            # Génère une réponse en utilisant le LLM
            answer = self.llm_service.generate_text(prompt, temperature)
            
            return answer
            
        except Exception as e:
            import traceback
            print(f"Erreur dans le service de connaissances DB avec contexte: {e}")
            print(traceback.format_exc())  
            return f"Erreur lors de la génération d'une réponse: {str(e)}"