"""Service for classifying queries to determine the best data source."""
from typing import Dict, Any, Tuple
from models.llm import LLMService

class QueryClassifierService:
    """Service for classifying user queries to determine the best data source."""
    
    def __init__(self, llm_service: LLMService):
        """Initialize the query classifier service.
        
        Args:
            llm_service: An initialized LLM service for query classification
        """
        self.llm_service = llm_service
        self.classification_types = [
            "tables", "views", "indexes", "foreign_keys", "vector_db"
        ]
    
    def classify_query(self, query: str) -> Tuple[str, float]:
        """Classify a query to determine the best data source.
        
        Args:
            query: The user's query text
            
        Returns:
            Tuple of (classification_type, confidence_score)
        """
        prompt = f"""Tu es un expert en intelligence artificielle qui aide à classifier les requêtes des utilisateurs sur une base de données.
Tu dois analyser la requête suivante et déterminer si elle concerne des tables, des vues, des index, des clés étrangères, ou si elle nécessite une recherche générale dans la base de connaissances vectorielle.

Requête de l'utilisateur : "{query}"

Réponds uniquement avec l'une des catégories suivantes, sans explications ni formatage supplémentaire :
- tables - si la requête demande des informations sur des tables, leur structure, ou des colonnes
- views - si la requête concerne des vues dans la base de données
- indexes - si la requête concerne des index dans la base de données
- foreign_keys - si la requête concerne des clés étrangères
- vector_db - si la requête nécessite une recherche générale dans la base de connaissances vectorielle

Classification :"""
        
        try:
            # Get classification from LLM
            response = self.llm_service.generate_text(prompt, temperature=0.1)
            response = response.strip().lower()
            
            # Determine which classification type is closest to the response
            for classification_type in self.classification_types:
                if classification_type in response:
                    confidence = 0.95  # High confidence if exact match
                    return classification_type, confidence
            
            # Default to vector_db if no clear classification
            return "vector_db", 0.7
        
        except Exception as e:
            print(f"Error classifying query: {e}")
            # Default to vector_db on error with lower confidence
            return "vector_db", 0.5
    
    def should_use_schema_metadata(self, query: str) -> bool:
        """Determine if schema metadata should be used for this query.
        
        Args:
            query: The user's query text
            
        Returns:
            Boolean indicating if schema metadata endpoints should be used
        """
        classification, confidence = self.classify_query(query)
        return classification != "vector_db" and confidence > 0.7