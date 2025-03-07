import requests

# Your APEX workspace details
workspace = "AI_DATABASE_ASSISTANT"
api_url = f"https://apex.oracle.com/pls/apex/ai_database_assistant/api/query/"

try:
    response = requests.get(api_url)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Parse and use the schema information
    if response.status_code == 200:
        tables = response.json()
        print("\nTables found:")
        for table in tables.get("tables", []):
            print(f"- {table.get('name')}")
except Exception as e:
    print(f"Error accessing REST API: {e}")