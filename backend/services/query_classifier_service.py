"""Service for classifying queries using LLM to determine database vs document content."""
from typing import Dict, Any, Tuple, List
from models.llm import LLMService
import json

class QueryClassifierService:
    """LLM-powered service for classifying user queries between APEX database and document content."""
    
    def __init__(self, llm_service: LLMService):
        """Initialize the query classifier service.
        
        Args:
            llm_service: An initialized LLM service for query classification
        """
        self.llm_service = llm_service
    
    def classify_query(self, query: str) -> Tuple[str, float, List[str]]:
        """Classify a query using LLM intelligence.
        
        Args:
            query: The user's query text
            
        Returns:
            Tuple of (classification_type, confidence_score, sub_types)
        """
        
        # Create a comprehensive prompt for the LLM
        classification_prompt = f"""Tu es un expert en classification de requêtes pour un système d'assistant IA qui a accès à deux sources de données distinctes :

1. **BASE DE DONNÉES ORACLE APEX** : Contient des métadonnées sur la structure technique d'une base de données (tables, vues, index, clés étrangères, colonnes)
2. **DOCUMENTS VECTORIELS** : Contient le contenu de documents téléchargés (CV, diplômes, PDFs, textes, transcriptions vidéo, texte extrait d'images)

Analyse cette requête utilisateur et détermine quelle source de données elle concerne :

**REQUÊTE UTILISATEUR :** "{query}"

**CRITÈRES DE CLASSIFICATION :**

**APEX DATABASE (structure technique) :**
- Questions sur les tables, vues, index, colonnes de la base de données
- Demandes de schéma de base de données
- Questions sur la structure technique des données
- Métadonnées de base de données
- Relations entre tables techniques

**DOCUMENT CONTENT (contenu des documents) :**
- Questions sur le contenu de documents téléchargés
- Recherche d'informations dans CV, diplômes, certificats
- Questions sur recrutement, emploi, formation
- Questions sur des organisations (ONCF, universités, entreprises)
- Recherche de contacts, informations personnelles
- Questions sur le contenu de vidéos transcrites
- Questions conceptuelles sur SQL/bases de données (explications)
- Toute question sur le CONTENU plutôt que la STRUCTURE

**EXEMPLES :**

APEX DATABASE:
- "Quelles sont les tables dans notre base de données ?"
- "Montre-moi le schéma de la base"
- "Lister les vues disponibles"
- "Quelles sont les clés étrangères ?"

DOCUMENT CONTENT:
- "ONCF il veut recruter quoi ?"
- "Qu'est-ce qui est écrit dans mon diplôme ?"
- "Comment optimiser une requête SQL ?" (explication conceptuelle)
- "Quels sont les contacts du recruteur ?"
- "Que dit mon CV sur mon expérience ?"

**INSTRUCTION :** Réponds avec un objet JSON exactement dans ce format :

{{
    "source": "apex_database" ou "document_content",
    "confidence": nombre entre 0 et 1,
    "reasoning": "explication courte de ton choix",
    "sub_category": "tables|views|indexes|foreign_keys|multi" (si apex_database) ou "content_search" (si document_content)
}}

Analyse maintenant la requête et réponds uniquement avec le JSON :"""

        try:
            # Get LLM response
            response = self.llm_service.generate_text(classification_prompt, temperature=0.1)
            
            # Try to parse JSON response
            try:
                # Clean the response to extract JSON
                response_clean = response.strip()
                if response_clean.startswith("```json"):
                    response_clean = response_clean.replace("```json", "").replace("```", "").strip()
                elif response_clean.startswith("```"):
                    response_clean = response_clean.replace("```", "").strip()
                
                # Parse JSON
                classification_result = json.loads(response_clean)
                
                source = classification_result.get("source", "document_content")
                confidence = float(classification_result.get("confidence", 0.7))
                reasoning = classification_result.get("reasoning", "")
                sub_category = classification_result.get("sub_category", "content_search")
                
                print(f"LLM Classification: {source} (confidence: {confidence:.2f}) - {reasoning}")
                
                # Convert to our expected format
                if source == "apex_database":
                    if sub_category == "multi":
                        return "multi", confidence, ["tables", "views", "indexes", "foreign_keys"]
                    else:
                        return sub_category, confidence, [sub_category]
                else:
                    return "vector_db", confidence, ["vector_db"]
                    
            except json.JSONDecodeError as e:
                print(f"Failed to parse LLM JSON response: {e}")
                print(f"Raw response: {response}")
                
                # Fallback: look for keywords in the raw response
                if "apex_database" in response.lower():
                    return "tables", 0.6, ["tables"]  # Conservative guess
                else:
                    return "vector_db", 0.8, ["vector_db"]  # Safe default
        
        except Exception as e:
            print(f"Error in LLM classification: {e}")
            
        # Ultimate fallback: assume document content (safer)
        return "vector_db", 0.7, ["vector_db"]
    
    def should_use_schema_metadata(self, query: str) -> bool:
        """Determine if schema metadata should be used for this query.
        
        Args:
            query: The user's query text
            
        Returns:
            Boolean indicating if schema metadata endpoints should be used
        """
        classification, confidence, _ = self.classify_query(query)
        return classification != "vector_db" and confidence > 0.6
    
    def get_multi_type_query_info(self, query: str) -> Dict[str, Any]:
        """Get detailed information for query classification.
        
        Args:
            query: The user's query text
            
        Returns:
            Dictionary with detailed classification information
        """
        classification, confidence, sub_types = self.classify_query(query)
        
        # Determine intent based on classification
        intent = self._detect_query_intent(query, classification)
        
        return {
            "classification": classification,
            "confidence": confidence,
            "sub_types": sub_types,
            "is_schema_query": classification != "vector_db" and confidence > 0.6,
            "intent_detected": intent
        }
    
    def _detect_query_intent(self, query: str, classification: str) -> str:
        """Detect the specific intent of the query.
        
        Args:
            query: The user's query text
            classification: The determined classification
            
        Returns:
            String describing the detected intent
        """
        query_lower = query.lower()
        
        if classification != "vector_db":
            # Database schema intents
            if any(word in query_lower for word in ["lister", "afficher", "montrer", "list", "show"]):
                return "list_schema_objects"
            elif any(word in query_lower for word in ["schéma", "structure", "schema", "complet"]):
                return "schema_information"
            else:
                return "database_metadata"
        else:
            # Document content intents
            if any(word in query_lower for word in ["recruter", "recrutement", "emploi", "travail", "poste"]):
                return "job_recruitment"
            elif any(word in query_lower for word in ["contact", "téléphone", "email", "coordonnées"]):
                return "contact_information"
            elif any(word in query_lower for word in ["diplôme", "certificat", "formation", "éducation"]):
                return "education_credentials"
            elif any(word in query_lower for word in ["comment", "how to", "expliquer", "explain"]):
                return "conceptual_explanation"
            elif any(word in query_lower for word in ["qu'est-ce que", "what is", "définition"]):
                return "definition_request"
            else:
                return "content_search"

    def explain_classification(self, query: str) -> str:
        """Get a human-readable explanation of why a query was classified a certain way.
        
        Args:
            query: The user's query text
            
        Returns:
            Human-readable explanation
        """
        classification_info = self.get_multi_type_query_info(query)
        
        if classification_info["is_schema_query"]:
            return f"Cette question concerne la structure technique de la base de données APEX (confiance: {classification_info['confidence']:.0%}). Je vais rechercher dans les métadonnées de la base de données."
        else:
            return f"Cette question concerne le contenu des documents téléchargés (confiance: {classification_info['confidence']:.0%}). Je vais rechercher dans la base de connaissances vectorielle."