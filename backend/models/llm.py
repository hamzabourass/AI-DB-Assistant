from langchain_community.llms import Ollama
import os
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    """Service pour interagir avec les modèles de langage."""
    
    def __init__(self):
        """Initialise le service LLM avec un modèle local."""
        
        # Configuration pour Ollama
        self.model_name = os.getenv("LOCAL_MODEL_NAME", "llama3.2:3b")  # Default to Llama 3.2 3B
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        try:
            # Initialize Ollama
            self.llm = Ollama(
                model=self.model_name,
                base_url=self.ollama_base_url,
                temperature=0.2,
                top_p=0.9,
                num_predict=4096,  # Max tokens
                num_ctx=4096,      # Context window
                repeat_penalty=1.1,
                num_thread=4       # Adjust based on your CPU cores
            )
            
            # Test the connection
            self._test_connection()
            
        except Exception as e:
            print(f"Error initializing Ollama: {e}")
            print("Make sure Ollama is installed and running!")
            print("Install: https://ollama.ai")
            print(f"Run: ollama pull {self.model_name}")
            raise ValueError(f"Failed to initialize Ollama: {str(e)}")
    
    def _test_connection(self):
        """Test if Ollama is running and model is available."""
        try:
            # Simple test query
            response = self.llm.invoke("Hi")
            print(f"Ollama connected successfully with model: {self.model_name}")
        except Exception as e:
            raise ValueError(f"Ollama connection test failed: {str(e)}")
    
    def generate_text(self, prompt, temperature=0.7):
        """Génère du texte basé sur le prompt fourni."""
        try:
            # Update temperature for this specific call
            self.llm.temperature = temperature
            
            response = self.llm.invoke(prompt)
            return response
        except Exception as e:
            print(f"Erreur lors de la génération de texte : {e}")
            return f"Une erreur s'est produite : {str(e)}"