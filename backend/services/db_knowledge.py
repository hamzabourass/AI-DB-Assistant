"""Service for answering database knowledge questions."""
from models.llm import LLMService


class DBKnowledgeService:
    """Service for answering database knowledge questions using LLM."""
    
    def __init__(self):
        """Initialize the DB Knowledge service."""
        self.llm_service = LLMService()
        self.knowledge_prompt_template = """You are an expert in databases and SQL. Answer the following question about databases, SQL, or data management:

Question: {question}

Provide a clear, accurate, and helpful answer. Include examples where appropriate to illustrate concepts. If you're unsure about any part of your answer, acknowledge the uncertainty rather than providing potentially incorrect information."""
    
    def answer_question(self, question, temperature=0.7):
        """Generate an answer to a database-related question."""
        try:
            prompt = self.knowledge_prompt_template.format(question=question)
            answer = self.llm_service.generate_text(prompt, temperature=temperature)
            
            if answer:
                return answer
            return "Error generating an answer to your question."
        except Exception as e:
            print(f"Error in DB knowledge service: {e}")
            return f"Error generating an answer: {str(e)}"