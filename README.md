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
  - [Installation de FFmpeg](#installation-de-ffmpeg)
- [Utilisation](#utilisation)
  - [Démarrage des services](#démarrage-des-services)
  - [Accès à l'interface](#accès-à-linterface)
- [Architecture RAG (Retrieval Augmented Generation)](#architecture-rag-retrieval-augmented-generation)
- [Technologies utilisées](#technologies-utilisées)
- [Structure du projet](#structure-du-projet)

## Vue d'ensemble

L'Assistant de Base de Données IA est une application qui permet aux utilisateurs de poser des questions sur les concepts de bases de données, de générer des requêtes SQL à partir de descriptions en langage naturel, et d'explorer des données structurées et non structurées grâce à une base de connaissances vectorielle.

L'application utilise une architecture moderne avec un backend FastAPI et un frontend Streamlit, avec une implémentation de la technique RAG (Retrieval Augmented Generation) pour fournir des réponses précises et contextuelles.

## Fonctionnalités

- **Assistant Base de Données** : Posez des questions sur les concepts de base de données, SQL et les techniques d'optimisation
- **Explorateur de Base Vectorielle** : Visualisez, recherchez et téléchargez des documents dans la base de connaissances vectorielle
- **Support multiformat** : Importation de connaissances à partir de divers formats de fichiers (TXT, PDF, DOCX, CSV, etc.)
- **Transcription de vidéos** : Extrayez et indexez automatiquement le contenu audio des vidéos pour enrichir la base de connaissances

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
- FFmpeg (pour la fonctionnalité de transcription vidéo)

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
# API Groq pour les modèles de langage
GROQ_API_KEY=votre_clé_api_groq

```

### Initialisation de la base vectorielle

Pour initialiser la base de données vectorielle avec des connaissances de base sur les bases de données :

```bash
cd backend
python scripts/initialize_db.py
```

Ce script va créer la base vectorielle et y indexer les documents présents dans le dossier `backend/knowledge`.

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

## Utilisation

### Démarrage des services

1. Démarrez le backend (dans un terminal) :

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

2. Démarrez le frontend (dans un autre terminal) :

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

### Accès à l'interface

Ouvrez votre navigateur et accédez à l'URL :

```
http://localhost:8501
```

## Architecture RAG (Retrieval Augmented Generation)

L'Assistant de Base de Données utilise l'architecture RAG (Retrieval Augmented Generation) pour améliorer la qualité des réponses générées par le modèle de langage. Voici comment fonctionne le processus :

Le diagramme ci-dessous illustre les interactions entre les différents composants du système:

![Diagramme d'interactions du système](./doc/diagram_rag.png)
1. **Indexation des documents** :
   - Les documents de connaissance sont divisés en chunks de taille appropriée
   - Chaque chunk est transformé en embedding vectoriel avec le modèle HuggingFace "all-MiniLM-L6-v2"
   - Les embeddings sont stockés dans une base de données vectorielle FAISS pour une recherche efficace

2. **Traitement des questions** :
   - La question de l'utilisateur est transformée en embedding vectoriel
   - Une recherche de similarité est effectuée dans la base FAISS pour récupérer les documents les plus pertinents
   - Les documents pertinents sont fusionnés avec la question dans un prompt enrichi

3. **Génération de réponse augmentée** :
   - Le modèle de langage (Mixtral 8x7B via Groq) reçoit le prompt enrichi
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
- **OpenAI Whisper** : Modèle de reconnaissance vocale pour la transcription vidéo
- **FFmpeg** : Outil de traitement audio/vidéo pour l'extraction d'audio

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
- **HuggingFace Embeddings** permettent d'utiliser des modèles d'embedding locaux, sans dépendance à des API externes
- **Whisper** offre une transcription de haute qualité en mode local
- **FFmpeg** est l'outil standard de l'industrie pour le traitement audio/vidéo, assurant une extraction audio fiable et de haute qualité

## Structure du projet

```
assistant-bdd-ia/
├── backend/
│   ├── app.py                   # Point d'entrée de l'API FastAPI
│   ├── database/                # Stockage des bases de données SQLite et vectorielles
│   ├── knowledge/               # Documents de connaissance à indexer
│   │   └── transcriptions/      # Transcriptions vidéo stockées
│   ├── models/                  # Modèles de données et de requêtes
│   ├── scripts/                 # Scripts utilitaires (initialisation, maintenance)
│   └── services/                # Services métier (SQL, RAG, historique, transcription)
│       └── video_transcription.py  # Service de transcription vidéo
├── frontend/
│   ├── app.py                   # Point d'entrée de l'application Streamlit
│   ├── modules/                 # Modules de l'interface utilisateur
│   │   └── video_transcription.py  # Interface de transcription vidéo
│   └── utils/                   # Utilitaires (connexion API, styles)
└── README.md                    # Documentation du projet
```