import requests

API_URL = "http://localhost:8000" 

def check_api_status():
    """Check if the backend API is available."""
    try:
        response = requests.get(f"{API_URL}/api/test", timeout=3)
        if response.status_code == 200:
            return {"connected": True, "status_code": response.status_code}
        else:
            return {"connected": False, "status_code": response.status_code}
    except requests.exceptions.ConnectionError:
        return {"connected": False, "status_code": None, "error": "Connection refused"}
    except requests.exceptions.Timeout:
        return {"connected": False, "status_code": None, "error": "Connection timeout"}
    except Exception as e:
        return {"connected": False, "status_code": None, "error": str(e)}

def generate_sql(description, dialect):
    """Generate SQL query from natural language description."""
    try:
        response = requests.post(
            f"{API_URL}/api/sql",
            json={"description": description, "dialect": dialect},
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "sql": response.json()["sql"]
            }
        else:
            return {
                "success": False,
                "error": f"Error: {response.status_code}",
                "message": response.text if response.text else "Unknown error"
            }
    except Exception as e:
        return {
            "success": False,
            "error": "Connection error",
            "message": str(e)
        }