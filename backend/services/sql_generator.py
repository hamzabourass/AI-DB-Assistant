from models.llm import LLMService
from langchain.prompts import PromptTemplate

class SQLGeneratorService:
    """Service for generating SQL queries from natural language."""
    
    def __init__(self):
        """Initialize the SQL generator service."""
        self.llm_service = LLMService()
        self.sql_prompt_template = """You are an expert SQL developer. Generate a {dialect} SQL query based on the following request:
            
Request: {description}
            
Provide only the SQL query without any explanation or comments. Ensure the SQL is valid and follows best practices for {dialect}."""
    
    def generate_sql(self, description, dialect="MySQL"):
        """Generate SQL from a natural language description."""
        try:
            prompt = self.sql_prompt_template.format(description=description, dialect=dialect)
            sql_query = self.llm_service.generate_text(prompt, temperature=0.1)
            
            if sql_query:
                # Remove markdown code formatting if present
                if "```sql" in sql_query:
                    sql_query = sql_query.split("```sql")[1].split("```")[0].strip()
                elif "```" in sql_query:
                    sql_query = sql_query.split("```")[1].split("```")[0].strip()
                
                return sql_query
            return "Error generating SQL query."
        except Exception as e:
            print(f"Error in SQL generation: {e}")
            return f"Error generating SQL query: {str(e)}"