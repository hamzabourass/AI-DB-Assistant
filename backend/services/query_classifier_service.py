"""Service for classifying queries to determine the best data source."""
from typing import Dict, Any, Tuple, List
from models.llm import LLMService

class QueryClassifierService:
    """Service for classifying user queries to determine the best data source."""
    
    def __init__(self, llm_service: LLMService):
        """Initialize the query classifier service.
        
        Args:
            llm_service: An initialized LLM service for query classification
        """
        self.llm_service = llm_service
        
        # Define classification types and their related keywords
        self.classification_types = {
            "tables": [
                "tables", "table", "database tables", "list tables", "show tables", 
                "what tables", "display tables", "table schema", "table structure"
            ],
            "views": [
                "views", "view", "database views", "list views", "show views", 
                "what views", "display views", "view definition"
            ],
            "indexes": [
                "indexes", "index", "database indexes", "list indexes", "show indexes", 
                "what indexes", "display indexes", "index structure"
            ],
            "foreign_keys": [
                "foreign keys", "foreign key", "fk", "list foreign keys", 
                "show foreign keys", "relationship", "table relationships"
            ],
            "multi": [
                "both", "all schema", "show schema", "database schema", 
                "everything", "all objects", "database objects"
            ],
            "vector_db": [
                "concept", "explain", "how to", "what is", "definition", 
                "example", "best practices", "optimize", "syntax"
            ]
        }
    
    def classify_query(self, query: str) -> Tuple[str, float, List[str]]:
        """Classify a query to determine the best data source.
        
        Args:
            query: The user's query text
            
        Returns:
            Tuple of (classification_type, confidence_score, sub_types)
            where sub_types is a list of secondary classification types
            for multi-object queries
        """
        query_lower = query.lower()
        
        # Check for multi-type queries first (those requesting multiple schema objects)
        if any(kw in query_lower for kw in self.classification_types["multi"]):
            # Check which specific types are mentioned
            mentioned_types = []
            for typ, keywords in self.classification_types.items():
                if typ != "multi" and typ != "vector_db":
                    if any(kw in query_lower for kw in keywords):
                        mentioned_types.append(typ)
            
            # If specific types are mentioned, return those
            if mentioned_types:
                return "multi", 0.9, mentioned_types
            
            # Otherwise, return all schema object types
            return "multi", 0.8, ["tables", "views", "indexes", "foreign_keys"]
        
        # For single-type queries, use more sophisticated classification with LLM
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
            response = self.llm_service.generate_text(prompt, temperature=0.1)
            response = response.strip().lower()
            
            for typ, keywords in self.classification_types.items():
                if any(kw in query_lower for kw in keywords):
                    return typ, 0.95, [typ]
            
            for typ in ["tables", "views", "indexes", "foreign_keys", "vector_db"]:
                if typ in response:
                    return typ, 0.85, [typ] 
            
            return "vector_db", 0.7, ["vector_db"]
        
        except Exception as e:
            print(f"Error classifying query: {e}")
            return "vector_db", 0.5, ["vector_db"]
    
    def should_use_schema_metadata(self, query: str) -> bool:
        """Determine if schema metadata should be used for this query.
        
        Args:
            query: The user's query text
            
        Returns:
            Boolean indicating if schema metadata endpoints should be used
        """
        classification, confidence, _ = self.classify_query(query)
        return classification != "vector_db" and confidence > 0.7
    
    def get_multi_type_query_info(self, query: str) -> Dict[str, Any]:
        """Get detailed information for multi-type queries.
        
        Args:
            query: The user's query text
            
        Returns:
            Dictionary with detailed classification information
        """
        classification, confidence, sub_types = self.classify_query(query)
        
        return {
            "classification": classification,
            "confidence": confidence,
            "sub_types": sub_types,
            "is_schema_query": classification != "vector_db" and confidence > 0.7
        }