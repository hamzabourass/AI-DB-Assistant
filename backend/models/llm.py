from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    """Service for interacting with Language Models."""
    
    def __init__(self):
        """Initialize the LLM service."""
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set in .env file")
        
        self.llm = ChatOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key="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",
            model_name="llama3-70b-8192",
            temperature=0.7
        )
    
    def generate_text(self, prompt, temperature=0.7):
        """Generate text based on the provided prompt."""
        try:
            # For backwards compatibility
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"Error generating text: {e}")
            return f"Error occurred: {str(e)}"