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
        
        # Define intent patterns for schema metadata queries
        self.schema_intent_patterns = {
            "tables": [
                "lister les tables", "afficher les tables", "quelles tables", 
                "montrer les tables", "tables disponibles", "noms des tables",
                "list tables", "show tables", "what tables", "available tables"
            ],
            "views": [
                "lister les vues", "afficher les vues", "quelles vues",
                "montrer les vues", "vues disponibles", "noms des vues",
                "list views", "show views", "what views", "available views"
            ],
            "indexes": [
                "lister les index", "afficher les index", "quels index",
                "montrer les index", "index disponibles", "noms des index",
                "list indexes", "show indexes", "what indexes", "available indexes"
            ],
            "foreign_keys": [
                "lister les clés étrangères", "afficher les clés étrangères", 
                "relations entre tables", "contraintes de clés étrangères",
                "list foreign keys", "show foreign keys", "table relationships"
            ],
            "multi": [
                "schéma de la base", "structure de la base", "tout le schéma",
                "objets de la base", "métadonnées complètes",
                "database schema", "show schema", "all objects", "complete metadata"
            ]
        }
        
        # Define patterns that indicate conceptual/syntax queries (vector_db)
        self.conceptual_patterns = [
            "comment", "how to", "pourquoi", "why", "qu'est-ce que", "what is",
            "expliquer", "explain", "définition", "definition", "exemple", "example",
            "syntaxe", "syntax", "optimiser", "optimize", "bonnes pratiques", "best practices",
            "différence entre", "difference between", "utiliser", "use", "créer", "create",
            "modifier", "modify", "supprimer", "delete", "insérer", "insert"
        ]
    
    def classify_query(self, query: str) -> Tuple[str, float, List[str]]:
        """Classify a query to determine the best data source.
        
        Args:
            query: The user's query text
            
        Returns:
            Tuple of (classification_type, confidence_score, sub_types)
            where sub_types is a list of secondary classification types
            for multi-object queries
        """
        query_lower = query.lower().strip()
        
        # First check if it's a conceptual/syntax question
        if any(pattern in query_lower for pattern in self.conceptual_patterns):
            return "vector_db", 0.9, ["vector_db"]
        
        # Use LLM for more sophisticated classification
        prompt = f"""Tu es un expert en classification de requêtes de base de données. Analyse la requête suivante et détermine son intention réelle.

Requête : "{query}"

Types de classification possibles :
- "tables" : L'utilisateur veut connaître quelles tables existent dans la base de données, leurs noms, ou leur structure/schéma
- "views" : L'utilisateur veut connaître quelles vues existent dans la base de données
- "indexes" : L'utilisateur veut connaître quels index existent dans la base de données  
- "foreign_keys" : L'utilisateur veut connaître les relations/clés étrangères entre les tables
- "multi" : L'utilisateur veut plusieurs types d'informations sur le schéma (tables + vues + index, etc.)
- "vector_db" : L'utilisateur pose une question conceptuelle, demande de l'aide sur la syntaxe SQL, ou cherche des explications générales

Exemples :
- "Quelles sont les tables dans ma base ?" → tables
- "Comment sélectionner toutes les colonnes d'une table ?" → vector_db (question de syntaxe)
- "Montrez-moi le schéma complet" → multi
- "Qu'est-ce qu'une clé étrangère ?" → vector_db (question conceptuelle)
- "Lister les vues disponibles" → views

Réponds uniquement avec le type de classification, sans explications :"""
        
        try:
            response = self.llm_service.generate_text(prompt, temperature=0.1)
            response = response.strip().lower()
            
            # Check for exact matches in LLM response
            valid_types = ["tables", "views", "indexes", "foreign_keys", "multi", "vector_db"]
            for typ in valid_types:
                if typ in response:
                    confidence = 0.85
                    
                    # Handle multi-type queries
                    if typ == "multi":
                        # Determine which sub-types are mentioned
                        mentioned_types = []
                        for schema_type, patterns in self.schema_intent_patterns.items():
                            if schema_type != "multi" and any(pattern in query_lower for pattern in patterns):
                                mentioned_types.append(schema_type)
                        
                        if mentioned_types:
                            return "multi", confidence, mentioned_types
                        else:
                            return "multi", confidence, ["tables", "views", "indexes", "foreign_keys"]
                    
                    return typ, confidence, [typ]
            
            # Fallback to pattern matching if LLM response is unclear
            for schema_type, patterns in self.schema_intent_patterns.items():
                if any(pattern in query_lower for pattern in patterns):
                    if schema_type == "multi":
                        return "multi", 0.8, ["tables", "views", "indexes", "foreign_keys"]
                    else:
                        return schema_type, 0.8, [schema_type]
            
            # Default to vector_db for unclear queries
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
            "is_schema_query": classification != "vector_db" and confidence > 0.7,
            "intent_detected": self._detect_query_intent(query)
        }
    
    def _detect_query_intent(self, query: str) -> str:
        """Detect the specific intent of the query for better classification.
        
        Args:
            query: The user's query text
            
        Returns:
            String describing the detected intent
        """
        query_lower = query.lower()
        
        # Check for specific intents
        if any(word in query_lower for word in ["comment", "how to"]):
            return "syntax_help"
        elif any(word in query_lower for word in ["qu'est-ce que", "what is", "définition", "definition"]):
            return "conceptual_explanation"
        elif any(word in query_lower for word in ["lister", "afficher", "montrer", "list", "show"]):
            return "list_objects"
        elif any(word in query_lower for word in ["schéma", "structure", "schema"]):
            return "schema_information"
        else:
            return "general_query"