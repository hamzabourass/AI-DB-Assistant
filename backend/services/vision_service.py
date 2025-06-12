"""
Service LLM spécialisé pour les modèles Vision multimodaux
"""
import os
import base64
import io
from PIL import Image
from groq import Groq
from dotenv import load_dotenv
from typing import List, Dict, Union, Optional

load_dotenv()

class VisionLLMService:
    """Service pour interagir avec les modèles de langage Vision multimodaux."""
    
    def __init__(self):
        """Initialise le service Vision LLM."""
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("La variable d'environnement GROQ_API_KEY n'est pas définie dans le fichier .env")
        
        self.client = Groq(api_key=api_key)
        self.vision_model = "meta-llama/llama-4-maverick-17b-128e-instruct"
        
        # Configuration par défaut
        self.default_temperature = 0.2
        self.default_max_tokens = 2048
        self.max_image_size = (1024, 1024)  # Taille max pour optimiser les performances
    
    def generate_text_with_image(
        self, 
        prompt: str, 
        image: Union[Image.Image, str, bytes], 
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """
        Génère du texte basé sur un prompt et une image.
        
        Args:
            prompt: Le prompt textuel
            image: Image PIL, chemin de fichier, ou bytes
            temperature: Température de génération (optionnel)
            max_tokens: Nombre max de tokens (optionnel)
            
        Returns:
            Texte généré par le modèle
        """
        try:
            # Convertir l'image en base64
            image_base64 = self._process_image(image)
            
            # Préparer les paramètres
            temp = temperature if temperature is not None else self.default_temperature
            max_tok = max_tokens if max_tokens is not None else self.default_max_tokens
            
            # Créer les messages avec image
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # Appel au modèle
            completion = self.client.chat.completions.create(
                model=self.vision_model,
                messages=messages,
                temperature=temp,
                max_tokens=max_tok
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"Erreur lors de la génération de texte avec image : {e}")
            return f"Une erreur s'est produite lors de l'analyse de l'image : {str(e)}"
    
    def generate_text_with_multiple_images(
        self, 
        prompt: str, 
        images: List[Union[Image.Image, str, bytes]], 
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """
        Génère du texte basé sur un prompt et plusieurs images.
        
        Args:
            prompt: Le prompt textuel
            images: Liste d'images (PIL, chemins, ou bytes)
            temperature: Température de génération (optionnel)
            max_tokens: Nombre max de tokens (optionnel)
            
        Returns:
            Texte généré par le modèle
        """
        try:
            # Préparer les paramètres
            temp = temperature if temperature is not None else self.default_temperature
            max_tok = max_tokens if max_tokens is not None else self.default_max_tokens
            
            content = [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
            
            for i, image in enumerate(images):
                image_base64 = self._process_image(image)
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_base64}"
                    }
                })
            
            messages = [
                {
                    "role": "user",
                    "content": content
                }
            ]
            
            completion = self.client.chat.completions.create(
                model=self.vision_model,
                messages=messages,
                temperature=temp,
                max_tokens=max_tok
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"Erreur lors de la génération de texte avec images multiples : {e}")
            return f"Une erreur s'est produite lors de l'analyse des images : {str(e)}"
    
    def analyze_graph(self, image: Union[Image.Image, str, bytes], context: str = "") -> Dict[str, str]:
        """
        Analyse spécialisée de graphiques avec prompt optimisé.
        
        Args:
            image: Image contenant le graphique
            context: Contexte additionnel (OCR, métadonnées, etc.)
            
        Returns:
            Dictionnaire structuré avec l'analyse du graphique
        """
        
        graph_prompt = f"""Tu es un expert en analyse de données visuelles. Analyse ce graphique/diagramme et fournis une description structurée.

{f"CONTEXTE ADDITIONNEL: {context}" if context else ""}

FOURNIS UNE ANALYSE STRUCTURÉE AVEC CES SECTIONS :

TYPE: [Identifie le type exact : graphique en barres, courbes, secteurs, tableau, diagramme, etc.]

STRUCTURE: [Décris la structure visuelle : axes, échelles, légendes, couleurs, disposition]

DONNÉES: [Liste les valeurs numériques, catégories, périodes que tu observes]

TENDANCES: [Identifie les tendances : croissance, baisse, cycles, pics, moyennes]

DOMAINE: [Détermine le domaine métier : finance, RH, ventes, production, marketing, etc.]

INSIGHTS: [Conclusions business importantes qu'on peut tirer de ces données]

QUALITÉ: [Évalue la lisibilité et la qualité de l'image]

Réponds en français avec ce format exact."""
        
        try:
            response = self.generate_text_with_image(
                prompt=graph_prompt,
                image=image,
                temperature=0.1,  
                max_tokens=1500
            )
            
            return self._parse_graph_analysis(response)
            
        except Exception as e:
            return {
                "error": f"Erreur analyse graphique : {str(e)}",
                "raw_response": ""
            }
    
    def compare_graphs(
        self, 
        images: List[Union[Image.Image, str, bytes]], 
        comparison_question: str = "Compare ces graphiques"
    ) -> str:
        """
        Compare plusieurs graphiques entre eux.
        
        Args:
            images: Liste d'images de graphiques à comparer
            comparison_question: Question spécifique de comparaison
            
        Returns:
            Analyse comparative des graphiques
        """
        
        comparison_prompt = f"""Tu es un expert en analyse comparative de données visuelles. 

QUESTION: {comparison_question}

Analyse ces graphiques et fournis une comparaison détaillée :

1. 📊 TYPES ET STRUCTURES : Compare les types de visualisations utilisées
2. 📈 DONNÉES ET ÉCHELLES : Compare les valeurs, unités, et échelles
3. 🔄 TENDANCES : Compare les évolutions et patterns
4. 💡 INSIGHTS COMPARATIFS : Quelles conclusions peut-on tirer de la comparaison ?
5. 🎯 RECOMMANDATIONS : Suggestions basées sur la comparaison

Réponds en français de manière structurée et détaillée."""
        
        return self.generate_text_with_multiple_images(
            prompt=comparison_prompt,
            images=images,
            temperature=0.2,
            max_tokens=2000
        )
    
    def _process_image(self, image: Union[Image.Image, str, bytes]) -> str:
        """
        Traite une image et la convertit en base64.
        
        Args:
            image: Image sous différents formats
            
        Returns:
            Image encodée en base64
        """
        try:
            if isinstance(image, Image.Image):
                pil_image = image
            
            elif isinstance(image, str):
                pil_image = Image.open(image)
            
            elif isinstance(image, bytes):
                pil_image = Image.open(io.BytesIO(image))
            
            else:
                raise ValueError(f"Format d'image non supporté : {type(image)}")
            
            if pil_image.size[0] > self.max_image_size[0] or pil_image.size[1] > self.max_image_size[1]:
                pil_image.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
            
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            buffer = io.BytesIO()
            pil_image.save(buffer, format='PNG', optimize=True)
            buffer.seek(0)
            
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Erreur traitement image : {str(e)}")
    
    def _parse_graph_analysis(self, response: str) -> Dict[str, str]:
        """
        Parse la réponse structurée d'analyse de graphique.
        
        Args:
            response: Réponse brute du modèle
            
        Returns:
            Dictionnaire avec les sections parsées
        """
        
        sections = {}
        current_section = None
        current_content = []
        
        for line in response.split('\n'):
            line = line.strip()
            
            section_keywords = ['TYPE', 'STRUCTURE', 'DONNÉES', 'TENDANCES', 'DOMAINE', 'INSIGHTS', 'QUALITÉ']
            
            for keyword in section_keywords:
                if line.startswith(f"{keyword}:"):
                    if current_section:
                        sections[current_section] = ' '.join(current_content).strip()
                    
                    current_section = keyword
                    current_content = [line.replace(f"{keyword}:", "").strip()]
                    break
            else:
                if current_section and line:
                    current_content.append(line)
        
        if current_section:
            sections[current_section] = ' '.join(current_content).strip()
        
        sections['raw_response'] = response
        
        return sections
    
    def get_available_models(self) -> List[str]:
        """Retourne la liste des modèles vision disponibles."""
        return [
            "meta-llama/llama-4-maverick-17b-128e-instruct",
        ]
    
    def test_connection(self) -> bool:
        """Teste la connexion au service Groq."""
        try:
            test_image = Image.new('RGB', (100, 100), color='white')
            
            response = self.generate_text_with_image(
                prompt="Décris cette image en un mot.",
                image=test_image,
                max_tokens=10
            )
            
            return "erreur" not in response.lower()
            
        except Exception as e:
            print(f"Test de connexion échoué : {e}")
            return False