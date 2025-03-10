import requests
import json

# Définir l'URL de l'API et la clé d'API (assurez-vous de la remplacer par la vôtre)
api_url = "https://api.groq.ai/v1/inference/llama70b424"
api_key = "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"

# Créez les données d'entrée pour l'API (le prompt pour le modèle)
data = {
    "inputs": {
        "text": "Voici un exemple de texte pour tester le modèle Llama70B424."
    }
}

# Créez les en-têtes pour la requête
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Envoyer la requête POST à l'API
response = requests.post(api_url, headers=headers, data=json.dumps(data))

# Vérifier la réponse
if response.status_code == 200:
    # Traiter la réponse JSON
    result = response.json()
    print("Réponse du modèle Llama70B424 :")
    print(result)
else:
    print(f"Erreur lors de l'appel à l'API: {response.status_code}")
    print(response.text)
