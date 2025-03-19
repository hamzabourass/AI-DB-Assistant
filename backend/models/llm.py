from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    """Service pour interagir avec les modèles de langage."""
    
    def __init__(self):
        """Initialise le service LLM."""
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("La variable d'environnement GROQ_API_KEY n'est pas définie dans le fichier .env")
        
        self.llm = ChatOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key,
            model_name="mixtral-8x7b-32768",
            temperature=0.2,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.0,
            max_tokens=4096
        )
    def generate_text(self, prompt, temperature=0.7):
        """Génère du texte basé sur le prompt fourni."""
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"Erreur lors de la génération de texte : {e}")
            return f"Une erreur s'est produite : {str(e)}"