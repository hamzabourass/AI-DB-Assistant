# Assistant de Base de Données IA

Une application moderne combinant interface Streamlit et intelligence artificielle pour répondre aux questions sur les bases de données, générer des requêtes SQL et explorer les données à partir de connaissances indexées dans une base vectorielle.


## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Configuration](#configuration)
  - [Prérequis](#prérequis)
  - [Installation](#installation)
  - [Configuration de l'environnement](#configuration-de-lenvironnement)
  - [Initialisation de la base vectorielle](#initialisation-de-la-base-vectorielle)
- [Utilisation](#utilisation)
  - [Démarrage des services](#démarrage-des-services)
  - [Accès à l'interface](#accès-à-linterface)
- [Guide d'utilisation des fonctionnalités](#guide-dutilisation-des-fonctionnalités)
  - [Page d'accueil](#page-daccueil)
  - [Assistant Base de Données](#assistant-base-de-données)
  - [Explorateur BDD Vectorielle](#explorateur-bdd-vectorielle)
  - [OCR et Extraction de Texte](#ocr-et-extraction-de-texte)
  - [Transcription Audio/Vidéo](#transcription-audiovideo)
  - [Maintenance Vectorielle](#maintenance-vectorielle)
- [Architecture RAG (Retrieval Augmented Generation)](#architecture-rag-retrieval-augmented-generation)
- [Technologies utilisées](#technologies-utilisées)
- [Structure du projet](#structure-du-projet)
- [Maintenance de la base vectorielle](#maintenance-de-la-base-vectorielle)

## Vue d'ensemble

L'Assistant de Base de Données IA est une application qui permet aux utilisateurs de poser des questions sur les concepts de bases de données, de générer des requêtes SQL à partir de descriptions en langage naturel, et d'explorer des données structurées et non structurées grâce à une base de connaissances vectorielle.

L'application utilise une architecture moderne avec un backend FastAPI et un frontend Streamlit, avec une implémentation de la technique RAG (Retrieval Augmented Generation) pour fournir des réponses précises et contextuelles.

## Fonctionnalités

- **Assistant Base de Données** : Posez des questions sur les concepts de base de données, SQL et les techniques d'optimisation
- **Explorateur de Base Vectorielle** : Visualisez, recherchez et téléchargez des documents dans la base de connaissances vectorielle
- **OCR Intelligent** : Extraction automatique de texte à partir d'images dans les documents (PDF, DOCX)
- **Transcription Audio/Vidéo** : Conversion automatique de contenu multimédia en texte indexable
- **Support multiformat** : Importation de connaissances à partir de divers formats de fichiers (TXT, PDF, DOCX, CSV, etc.)
- **Maintenance vectorielle** : Interface d'administration pour gérer les fichiers de connaissances et optimiser la base vectorielle

## Architecture

L'application est composée de deux modules principaux :

1. **Backend (FastAPI)** : API REST fournissant les services d'IA et d'accès aux données
2. **Frontend (Streamlit)** : Interface utilisateur interactive et réactive

La communication entre les deux modules se fait via des appels API REST.

## Configuration

### Prérequis

- Python 3.9+ 
- pip (gestionnaire de packages Python)
- Accès à l'API Groq (ou autre service de LLM compatible)
- FFmpeg (pour la transcription vidéo)
- Tesseract OCR (optionnel, pour améliorer l'extraction de texte)

### Installation

1. Clonez le dépôt :

```bash
git clone https://github.com/votre-compte/assistant-bdd-ia.git
cd assistant-bdd-ia
```

2. Créez et activez un environnement virtuel :

```bash
# Sous Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Sous Windows
python -m venv venv
venv\Scripts\activate
```

3. Installez les dépendances :

```bash
# Installez les dépendances du backend
cd backend
pip install -r requirements.txt

# Installez les dépendances du frontend
cd ../frontend
pip install -r requirements.txt
```

### Configuration de l'environnement

1. Créez un fichier `.env` dans le dossier `backend` :

```bash
cd ../backend
# Cree un fichier `.env` dans le dossier `backend`
```

2. Ajoutez vos clés API et configurez les variables d'environnement dans le fichier `.env` :

```
# Va sur https://console.groq.com/, connecte-toi, puis crée une clé API dans la section "API Keys" et cree un api key
# API Groq pour les modèles de langage
GROQ_API_KEY=votre_clé_api_groq

```
### Configuration avec Groq (Recommandé pour la performance)

Groq offre un accès rapide aux modèles LLM dans le cloud :
1. Créez un compte sur [console.groq.com](https://console.groq.com/)
2. Générez une clé API dans la section "API Keys"
3. Ajoutez la clé dans votre fichier `.env`

### Configuration avec Ollama (Alternative locale)

Pour utiliser Ollama en local (gratuit mais plus lent) :

#### Installation d'Ollama
```bash
# Linux/WSL
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama

# Windows : Téléchargez depuis ollama.com
```

#### Démarrage et configuration
```bash
# Démarrer le service
ollama serve

# Dans un nouveau terminal, télécharger le modèle
ollama pull llama3.2:3b

# Vérifier l'installation
ollama list
```

#### Modèles recommandés
```bash
# Pour de meilleures performances (si vous avez assez de RAM)
ollama pull llama3.2:8b     # 8B paramètres - Beaucoup mieux
ollama pull qwen2.5:7b      # 7B paramètres - Très bon
ollama pull mistral:7b      # 7B paramètres - Excellent pour le français
```

Puis modifiez votre `.env` :
```env
LOCAL_MODEL_NAME=llama3.2:8b  # ou le modèle choisi
```

## Conteneurisation Oracle + APEX avec uc-local-apex-dev

Ce projet GitHub propose une installation prête à l'emploi d'Oracle XE 23c + APEX + ORDS dans des conteneurs Docker, pour un environnement de développement local.

## Prérequis

- **Docker Desktop** doit être installé et en cours d'exécution sur votre machine
- Git (pour cloner le dépôt)

## Étapes détaillées d'installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/United-Codes/uc-local-apex-dev.git
cd uc-local-apex-dev
```

### 2. Initialiser l'environnement

Dans la ligne de commande PowerShell ou CMD, lancez le script :

```bash
./setup.sh
```

> **Note :** Ce script prépare les dossiers, permissions et volumes nécessaires pour Docker.

### 3. Démarrer les conteneurs

Lancez la commande suivante pour démarrer les conteneurs :

```bash
docker compose up -d
```

Cette commande va :
- Démarrer Oracle XE avec APEX installé
- Configurer ORDS pour accéder à APEX via HTTP
- L'installation initiale peut durer plusieurs minutes

### 4. Surveiller l'installation

Pour suivre le processus d'installation en temps réel :

```bash
docker compose logs -f ords
```

Attendez un message de confirmation comme **"ORDS started"**.

### Configuration Oracle APEX (Optionnel - pour les métadonnées de schéma)

Si vous souhaitez interroger les métadonnées de votre base de données Oracle APEX :

#### Configuration du Workspace et API REST

1. **Accéder à APEX** : http://localhost:8080/ords
   - Cliquez sur "OK" pour Oracle APEX
   - Connectez-vous avec : Workspace `INTERNAL`, User `ADMIN`, Password `Welcome_1`

2. **Créer un workspace** :
   
   a) Cliquez sur "Manage Workspaces" dans la page d'accueil :
   ![Manage Workspaces](/docs/screenshots/workspapce1.png)
   
   b) Cliquez sur "Create Workspace" :
   ![Create Workspace](/docs/screenshots/workspace2.png)
   
   c) Remplissez les informations de création :
   ![Workspace Info](/docs/screenshots/workspace3.png)
   
   d) Sélectionnez "Non" pour utiliser un schéma existant et remplissez le nom :
   ![Schema Creation](/docs/screenshots/workspace4.png)
   
   e) Créez les identifiants du workspace :
   ![Workspace Credentials](/docs/screenshots/workspace5.png)

3. **Se connecter au nouveau workspace** :
   
   Déconnectez-vous du compte admin et connectez-vous avec le workspace créé :
   ![Workspace Login](/docs/screenshots/workspace6.png)

4. **Importer des données d'exemple** :
   
   a) Allez dans "SQL Workshop" :
   ![SQL Workshop](/docs/screenshots/workspace7.png)
   
   b) Cliquez sur "Utilities" → "Sample Datasets" et téléchargez une base de données

5. **Créer l'API REST pour les métadonnées** :
   
   a) Dans "SQL Workshop" → "RESTful Services" et activez REST pour le schéma :
   ![Enable REST](/docs/screenshots/workspace8.png)
   
   b) Dans le sidebar à gauche, cliquez sur "Modules" :
   ![Modules](/docs/screenshots/module.png)
   
   c) Cliquez sur "Create Module" :
   ![Create Module](/docs/screenshots/createModule.png)
   
   d) Donnez un nom au module et le base path :
   ![Module Info](/docs/screenshots/remplireModule.png)
   
   e) Dans le module, cliquez sur "Create Template" :
   ![Create Template](/docs/screenshots/createTemplate.png)
   
   f) Remplissez l'URI template qui représente la ressource à retourner :
   ![Template Info](/docs/screenshots/remplireTemplate.png)
   
   g) Dans le template, créez un handler :
   ![Create Handler](/docs/screenshots/createHandler.png)
   
   h) Remplissez les informations du handler et ajoutez le script PL/SQL :
   ![Handler Info](/docs/screenshots/remplireHandler.png)

```sql
DECLARE
  v_schema VARCHAR2(30) := USER;
  v_table_count NUMBER;
BEGIN
  APEX_JSON.INITIALIZE_OUTPUT(p_http_header => TRUE);
  APEX_JSON.OPEN_OBJECT;
  
  SELECT COUNT(*) INTO v_table_count FROM user_tables;
  
  APEX_JSON.WRITE('schema', v_schema);
  APEX_JSON.WRITE('total_tables', v_table_count);
  
  APEX_JSON.OPEN_ARRAY('tables');
  FOR t IN (SELECT table_name, num_rows FROM user_tables ORDER BY table_name) LOOP
    APEX_JSON.OPEN_OBJECT;
    APEX_JSON.WRITE('name', t.table_name);
    APEX_JSON.WRITE('rows', NVL(t.num_rows, 0));
    
    APEX_JSON.OPEN_ARRAY('columns');
    FOR c IN (
      SELECT column_name, data_type, column_id
      FROM user_tab_columns
      WHERE table_name = t.table_name
      AND column_id <= 5
      ORDER BY column_id
    ) LOOP
      APEX_JSON.OPEN_OBJECT;
      APEX_JSON.WRITE('name', c.column_name);
      APEX_JSON.WRITE('type', c.data_type);
      APEX_JSON.CLOSE_OBJECT;
    END LOOP;
    APEX_JSON.CLOSE_ARRAY;
    
    APEX_JSON.CLOSE_OBJECT;
  END LOOP;
  APEX_JSON.CLOSE_ARRAY;
  
  APEX_JSON.CLOSE_OBJECT;
  
EXCEPTION
  WHEN OTHERS THEN
    APEX_JSON.INITIALIZE_OUTPUT(p_http_header => TRUE);
    APEX_JSON.OPEN_OBJECT;
    APEX_JSON.WRITE('error', SQLERRM);
    APEX_JSON.CLOSE_OBJECT;
END;
```

5. **Tester l'API** :
   
   Prenez l'URL complète et testez l'endpoint :
   ![Full URL](/docs/screenshots/fullURL.png)
   
   Résultat de l'appel API :
   ![API Result](/docs/screenshots/appel.png)

6. **Configurer le backend** :
   
   Dans `backend/services/schema_metadata_service.py`, mettez à jour l'URL :
   ```python
   self.base_url = "http://localhost:8080/ords/restworkspace/schema"
   ```

#### Option 2 : Connexion à une instance existante

Si vous avez déjà Oracle APEX déployé :
```python
self.base_url = "http://votre-apex-server:port/ords/votre-workspace/schema"
```

**Note importante :** La fonctionnalité APEX est optionnelle. L'application fonctionne parfaitement sans elle en utilisant uniquement la base vectorielle pour répondre aux questions sur les bases de données.

## Commandes utiles

### Gestion des conteneurs

```bash
# Démarrer les conteneurs
docker compose up -d

# Arrêter les conteneurs
docker compose down

# Voir les logs en temps réel
docker compose logs -f

# Voir le statut des conteneurs
docker compose ps

# Redémarrer les services
docker compose restart
```

### Accès aux bases de données

```bash
# Se connecter à Oracle XE via SQL*Plus dans le conteneur
docker compose exec oracle sqlplus sys/Welcome_1@XE as sysdba

# Accéder au shell du conteneur Oracle
docker compose exec oracle bash
```
### Initialisation de la base vectorielle

Pour initialiser la base de données vectorielle avec des connaissances de base sur les bases de données :

```bash
cd backend
python scripts/initialize_db.py
```
Ce script va créer la base vectorielle et y indexer les documents présents dans le dossier `backend/knowledge`.

Nous avons créé le schéma de données Customer Order à partir de deux datasets dans Oracle APEX, comme illustré dans l'image ci-dessus.

![alt text](/docs/apexdataset.png)
Le fichier du schéma se trouve dans le dossier : `/backend/knowledge/`


### Installation de FFmpeg

FFmpeg est nécessaire pour la fonctionnalité de transcription vidéo. Voici comment l'installer selon votre système d'exploitation :

#### Windows (avec Chocolatey)

1. Installer Chocolatey si ce n'est pas déjà fait :
   - Ouvrez PowerShell en tant qu'administrateur
   - Exécutez la commande :
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

2. Installer FFmpeg avec Chocolatey :
   ```powershell
   choco install ffmpeg
   ```

3. Vérifier l'installation :
   ```powershell
   ffmpeg -version
   ```

#### Windows (installation manuelle)

1. Téléchargez FFmpeg depuis [le site officiel](https://ffmpeg.org/download.html) (version "Windows builds")
2. Extrayez l'archive téléchargée
3. Ajoutez le dossier `bin` à votre variable d'environnement PATH
4. Vérifiez l'installation en ouvrant une nouvelle invite de commande et en tapant `ffmpeg -version`

#### macOS

Avec Homebrew :
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install ffmpeg
```

#### Vérification

Pour vérifier que FFmpeg est correctement installé, exécutez :
```bash
ffmpeg -version
```

### Installation de Tesseract OCR (Optionnel)

Tesseract améliore la qualité d'extraction de texte des images. Installation selon votre système :

#### Windows
```powershell
# Avec Chocolatey
choco install tesseract

# Ou téléchargement manuel depuis:
# https://github.com/UB-Mannheim/tesseract/wiki
```

#### macOS
```bash
brew install tesseract tesseract-lang
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt install tesseract-ocr tesseract-ocr-fra
```

## Utilisation

### Démarrage des services

1. Démarrez le backend (dans un terminal) :

```bash
cd backend
uvicorn app:app --reload --port 8000
```

2. Démarrez le frontend (dans un autre terminal) :

```bash
cd frontend
streamlit run app.py
```

### Accès à l'interface

Ouvrez votre navigateur et accédez à l'URL :

```
http://localhost:8501
```

## Guide d'utilisation des fonctionnalités

### Page d'accueil

![Page d'accueil](/docs/screenshots/home.png)

La page d'accueil vous présente une vue d'ensemble de l'application avec :

- **Présentation générale** : Une introduction aux fonctionnalités de l'application
- **Cartes de fonctionnalités** : Les différents modules disponibles
- **État du système** : Indicateur de l'état de connexion à l'API backend
- **Démarrage rapide** : Instructions pour commencer à utiliser l'application

**Pour naviguer dans l'application** :
- Utilisez le menu de navigation dans la barre latérale gauche
- Chaque menu vous dirige vers une fonctionnalité spécifique de l'application

### Assistant Base de Données

![Assistant BDD](/docs/screenshots/assistant.png)

L'Assistant de Base de Données vous permet d'interagir en langage naturel pour :

- **Poser des questions** sur la base donnee RAG et les concepts de bases de données
- **Obtenir des explications** sur la syntaxe SQL
- **Demander des conseils** sur les techniques d'optimisation
- **Générer des requêtes SQL** à partir de descriptions en langage naturel

**Comment utiliser l'Assistant** :
1. Tapez votre question dans le champ de texte en bas de l'écran
2. Cliquez sur "Envoyer" ou appuyez sur Entrée
3. L'assistant analysera votre question et fournira une réponse contextualisée
4. Les conversations sont automatiquement sauvegardées pour référence future

**Exemples de questions** :
- "Quel est le schéma de notre base de données ?"
- "Comment optimiser une requête qui fait plusieurs jointures ?"
- "Génère une requête SQL pour trouver tous les produits avec un prix plus de 20"
- "Explique-moi la différence entre INNER JOIN et LEFT JOIN"

### Explorateur BDD Vectorielle

![Explorateur BDD Vectorielle](/docs/screenshots/explorer.png)

L'Explorateur de Base de Données Vectorielle vous permet de :

#### Onglet Aperçu
- **Visualiser les statistiques** de la base vectorielle (nombre de documents, dimensions, etc.)
- **Consulter la répartition** des sources de documents dans un graphique
- **Télécharger de nouveaux documents** à ajouter à la base de connaissances

**Pour télécharger un document** :
1. Cliquez sur "Parcourir les fichiers" ou faites glisser votre fichier dans la zone
2. Vérifiez les détails du fichier
3. Cliquez sur "Télécharger et Indexer le Document"
4. Attendez que l'indexation soit terminée

![Téléchargement de documents](/docs/screenshots/upload.png)

#### Onglet Explorateur de Documents
- **Parcourir tous les documents** indexés dans la base vectorielle
- **Consulter les métadonnées** et le contenu de chaque document
- **Naviguer entre les pages** de résultats

![Exploration de documents](/docs/screenshots/documents.png)

#### Onglet Recherche
- **Rechercher du contenu** dans la base vectorielle en langage naturel
- **Ajuster le nombre de résultats** à afficher
- **Consulter les documents** les plus pertinents pour votre recherche avec leur score de similarité

![Recherche vectorielle](/docs/screenshots/search.png)

### OCR et Extraction de Texte

#### Architecture OCR
![alt text](/docs/Architecture_OCR.png)
Le module OCR (Optical Character Recognition) permet d'extraire automatiquement le texte des images contenues dans vos documents :

#### Fonctionnalités OCR
- **Extraction automatique** : Le texte des images dans les PDF et DOCX est automatiquement extrait lors du téléchargement
- **Multi-moteurs** : Utilise EasyOCR et Tesseract pour une précision optimale
- **Multi-langues** : Support du français, anglais, espagnol, allemand
- **Prétraitement intelligent** : Amélioration automatique de la qualité des images pour une meilleure reconnaissance
- **Indexation transparente** : Le texte extrait est automatiquement ajouté à la base vectorielle

#### Types d'images supportées
- **Documents scannés** : Anciennes factures, contrats, lettres
- **Diagrammes** : Schémas de base de données, organigrammes
- **Screenshots** : Captures d'écran de code, interfaces, erreurs
- **Certificats** : Diplômes, attestations, certifications
- **Notes manuscrites** : Notes de réunion, croquis annotés

#### Processus OCR automatique
1. **Détection** : Le système détecte automatiquement les images dans les documents téléchargés
2. **Extraction** : Les images sont extraites du document
3. **Prétraitement** : Amélioration de contraste, réduction du bruit, binarisation
4. **Reconnaissance** : Application de multiples moteurs OCR avec différents paramètres
5. **Sélection** : Choix du meilleur résultat basé sur la confiance
6. **Indexation** : Intégration du texte extrait dans la base vectorielle

#### Indicateurs de qualité
- **Scores de confiance** : Pourcentage de fiabilité de l'extraction
- **Méthode utilisée** : Quel moteur OCR a donné le meilleur résultat
- **Taille d'image** : Résolution des images traitées
- **Langue détectée** : Langue(s) reconnue(s) dans le texte

### Transcription Audio et Vidéo

Le module de Transcription Audio et Vidéo vous permet de :

#### Onglet Télécharger
- **Transcription automatique** des fichiers vidéo et audio
- **Choix du modèle** de transcription selon vos besoins (taille/précision)
- **Indexation automatique** des transcriptions dans la base vectorielle

**Pour transcription un fichier audio ou vidéo** :
1. Sélectionnez le modèle de transcription approprié
   - `tiny` : Le plus rapide, moins précis (1GB VRAM)
   - `base` : Bon équilibre vitesse/précision (1GB VRAM)
   - `small` : Plus précis, plus lent (2GB VRAM)
   - `medium` : Haute précision, lent (5GB VRAM)
   - `large` : La plus haute précision, très lent (10GB VRAM)
2. Téléchargez votre fichier vidéo (MP4, AVI, MOV, MKV, WebM) ou audio (MP3, WAV, OGG, M4A)
3. Cliquez sur "Transcription et indexation"
4. Attendez que le traitement soit terminé

![Téléchargement de fichiers](/docs/screenshots/transcription-upload.png)

#### Onglet Liste des Transcriptions
- **Consultez toutes les transcriptions** disponibles
- **Visualisez le contenu** de chaque transcription
- **Accédez facilement** aux transcriptions précédentes

![Liste des transcriptions](/docs/screenshots/transcription-list.png)

#### Onglet Recherche
- **Navigation vers l'explorateur vectoriel** pour rechercher dans les transcriptions
- **Interrogation via l'assistant** pour obtenir des réponses basées sur vos transcriptions

**Formats pris en charge** :
- **Vidéo** : MP4, AVI, MOV, MKV, WebM
- **Audio** : MP3, WAV, OGG, M4A

**Conseils d'utilisation** :
- Pour de meilleurs résultats, utilisez des enregistrements avec un bon rapport signal/bruit
- Les modèles plus grands sont plus précis mais nécessitent plus de ressources
- La transcription s'intègre automatiquement à la base de connaissances et devient interrogeable

### Maintenance Vectorielle

![Maintenance Vectorielle](/docs/screenshots/maintenance.png)

La page de Maintenance Vectorielle est un outil d'administration permettant de :

#### Onglet Fichiers de Connaissance
- **Voir tous les fichiers** présents dans la base de connaissances
- **Filtrer les fichiers** par catégorie
- **Supprimer des fichiers** individuellement ou par catégorie
- **Créer des sauvegardes** de tous les fichiers

**Pour supprimer un fichier** :
1. Sélectionnez le fichier dans la liste déroulante
2. Cliquez sur "Supprimer le fichier sélectionné"
3. Confirmez la suppression

![Gestion des fichiers](/docs/screenshots/files.png)

#### Onglet Base Vectorielle
- **Vider la base vectorielle** sans supprimer les fichiers source
- **Réindexer tous les fichiers** pour reconstruire la base vectorielle
- **Consulter les statistiques** détaillées de la base vectorielle
- **Voir des recommandations** pour optimiser les performances

![Gestion de la base vectorielle](/docs/screenshots/vectordb.png)
![Gestion de la base vectorielle](/docs/screenshots/vectordb2.png)

#### Onglet Réinitialisation Complète
- **Réinitialiser entièrement** le système (avec création automatique d'une sauvegarde)
- **Supprimer tous les fichiers** et vider la base vectorielle
- **Accéder aux informations de diagnostic** pour résoudre les problèmes

**Attention** : Cette section contient des actions destructives qui ne peuvent pas être annulées. Utilisez avec précaution !

![Réinitialisation du système](/docs/screenshots/reset.png)

## Architecture RAG (Retrieval Augmented Generation)

L'Assistant de Base de Données utilise l'architecture RAG (Retrieval Augmented Generation) pour améliorer la qualité des réponses générées par le modèle de langage. Voici comment fonctionne le processus :

Le diagramme ci-dessous illustre les interactions entre les différents composants du système:

![Diagramme d'interactions du système](./docs/image.png)

1. **Indexation des documents** :
   - Les documents de connaissance sont divisés en chunks de taille appropriée
   - Chaque chunk est transformé en embedding vectoriel avec le modèle HuggingFace "all-MiniLM-L6-v2"
   - Les embeddings sont stockés dans une base de données vectorielle FAISS pour une recherche efficace

2. **Traitement des questions** :
   - La question de l'utilisateur est transformée en embedding vectoriel
   - Une recherche de similarité est effectuée dans la base FAISS pour récupérer les documents les plus pertinents
   - Les documents pertinents sont fusionnés avec la question dans un prompt enrichi

3. **Génération de réponse augmentée** :
   - Le modèle de langage (llama-3.3-70b-versatile) reçoit le prompt enrichi
   - Le contexte supplémentaire aide le modèle à générer une réponse plus précise et factuelle
   - L'historique de conversation est également inclus pour maintenir la cohérence des échanges

4. **Gestion de la mémoire de conversation** :
   - Les conversations longues sont automatiquement résumées pour rester dans les limites du contexte
   - Les résumés préservent les informations techniques importantes

Cette architecture permet à l'assistant de fournir des réponses plus précises sur les bases de données en s'appuyant sur des connaissances indexées plutôt que sur les seules connaissances du modèle de base.

## Technologies utilisées

### Backend
- **FastAPI** : Framework API web moderne et performant
- **Langchain** : Bibliothèque pour construire des applications avec des LLM
- **FAISS** : Bibliothèque de recherche de similarité vectorielle développée par Facebook AI
- **SQLAlchemy** : ORM pour la gestion des données relationnelles
- **HuggingFace Embeddings** : Modèles de transformation de texte en vecteurs
- **Groq API** : Service d'inférence pour les grands modèles de langage

#### Technologies OCR
- **EasyOCR** : Moteur OCR moderne basé sur l'IA, précis et multi-langue
- **Tesseract** : Moteur OCR traditionnel open-source de Google (optionnel)
- **OpenCV** : Bibliothèque de vision par ordinateur pour le prétraitement d'images
- **Pillow (PIL)** : Manipulation et amélioration d'images Python
- **PyMuPDF (fitz)** : Extraction d'images et de texte à partir de documents PDF
- **python-docx** : Traitement de documents Word pour l'extraction d'images

#### Technologies de Transcription
- **Whisper** : Modèle de transcription automatique de la parole d'OpenAI
- **FFmpeg** : Traitement et conversion de fichiers multimédia

### Frontend
- **Streamlit** : Framework pour créer des applications frontend avec python
- **Pandas** : Manipulation et analyse de données
- **Matplotlib** : Visualisation de données
- **Requests** : Client HTTP pour communiquer avec l'API

### Pourquoi ces technologies ?

- **FastAPI** a été choisi pour sa performance et sa facilité d'intégration avec les modèles ML
- **Streamlit** permet de créer rapidement des interfaces utilisateur réactives 
- **FAISS** offre des performances exceptionnelles pour la recherche vectorielle à grande échelle
- **Langchain** simplifie l'intégration des LLM dans les workflows d'applications
- **Groq API** fournit un accès rapide aux LLM 
- **Model local llama3.2 3b** petit model qui marche sur le CPU
- **HuggingFace Embeddings** permettent d'utiliser des modèles d'embedding locaux, sans dépendance à des API externes
- **EasyOCR** combine précision et facilité d'utilisation pour l'extraction de texte multi-langue
- **Whisper** offre une transcription de haute qualité pour de nombreuses langues
- **OpenCV** et **Pillow** permettent un prétraitement d'images sophistiqué pour améliorer la qualité OCR

## Structure du projet

```
assistant-bdd-ia/
├── backend/
│   ├── app.py                   # Point d'entrée de l'API FastAPI
│   ├── database/                # Stockage des bases de données SQLite et vectorielles
│   │   └── backups/             # Sauvegardes des fichiers de connaissance
│   ├── knowledge/               # Documents de connaissance à indexer
│   │   ├── ocr_texts/           # Textes extraits par OCR (généré automatiquement)
│   │   └── transcriptions/      # Transcriptions audio/vidéo (généré automatiquement)
│   ├── models/                  # Modèles de données et de requêtes
│   ├── scripts/                 # Scripts utilitaires (initialisation, maintenance)
│   └── services/                # Services métier
│       ├── vector_db.py         # Service de base vectorielle principal
│       ├── document_ocr_service.py  # Service OCR pour extraction de texte
│       ├── video_transcription.py   # Service de transcription audio/vidéo
│       ├── db_knowledge.py      # Service RAG principal
│       └── vector_db_cleanup.py # Service de nettoyage de la base vectorielle
├── frontend/
│   ├── app.py                   # Point d'entrée de l'application Streamlit
│   ├── modules/                 # Modules de l'interface utilisateur
│   │   ├── vector_db_explorer.py   # Interface d'exploration avec support OCR
│   │   ├── video_transcription.py  # Interface de transcription
│   │   └── vector_db_cleanup.py    # Interface de maintenance vectorielle
│   └── utils/                   # Utilitaires (connexion API, styles)
├── docs/
│   ├── image.png                # Diagramme d'architecture
│   ├── ocr_architecture.png     # Diagramme d'architecture OCR
│   └── screenshots/             # Captures d'écran de l'application
└── README.md                    # Documentation du projet
```

## Maintenance de la base vectorielle

La maintenance régulière de la base vectorielle est importante pour maintenir des performances optimales :

### Indexation OCR
- Les textes extraits par OCR sont automatiquement indexés lors du téléchargement de documents
- Le système détecte automatiquement les images dans les PDF et DOCX
- Les résultats OCR sont marqués avec des métadonnées spéciales pour identification

### Surveillance de la qualité OCR
- Surveillez les scores de confiance dans les logs
- Les textes avec une confiance < 0.3 ne sont pas indexés automatiquement
- Réajustez les paramètres de prétraitement si nécessaire

### Optimisation des performances
- Les documents avec de nombreuses images peuvent augmenter le temps d'indexation
- Utilisez des images de bonne qualité pour de meilleurs résultats OCR
- Considérez l'upgrade vers un GPU pour accélérer EasyOCR

### Nettoyage périodique
- Supprimez les anciens textes OCR peu fiables
- Réindexez périodiquement pour optimiser la base vectorielle
- Utilisez l'interface de maintenance pour surveiller l'espace disque