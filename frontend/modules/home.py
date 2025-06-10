import streamlit as st
from utils.api import check_api_status

def render_home_page():
    """Affiche la page d'accueil de l'application."""
    # Titre principal
    st.title("Assistant Base de Données IA")
    
    # Carte d'introduction
    st.markdown("""
    <div style="
        padding: 20px; 
        border-radius: 8px; 
        background-color: white; 
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    ">
        <h3>Bienvenue sur l'Assistant Base de Données IA 👋</h3>
        <p>Cet outil vous aide à travailler plus efficacement avec les bases de données en utilisant l'intelligence artificielle.
        Que vous ayez besoin d'écrire des requêtes SQL, d'apprendre des concepts de base de données ou de concevoir des schémas,
        nous sommes là pour vous aider.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Section Fonctionnalités
    st.markdown("""
    <h2 style="margin-top: 30px; margin-bottom: 20px;">Fonctionnalités</h2>
    """, unsafe_allow_html=True)
    
    # Fonctionnalités dans une mise en page de cartes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            padding: 20px; 
            border-radius: 8px; 
            background-color: white; 
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            height: 100%;
        ">
            <div style="font-size: 2rem; margin-bottom: 10px;">💬</div>
            <h3>Assistant BDD</h3>
            <p>Posez des questions sur les bases de données et SQL.</p>
            <div style="
                display: inline-block;
                padding: 4px 8px;
                background-color: #e6f4ea;
                color: #137333;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: 500;
            ">
                Disponible
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            padding: 20px; 
            border-radius: 8px; 
            background-color: white; 
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            height: 100%;
        ">
            <div style="font-size: 2rem; margin-bottom: 10px;">🔍</div>
            <h3>Explorateur BDD Vectorielle</h3>
            <p>Explorez et recherchez dans la base de connaissances vectorielle.</p>
            <div style="
                display: inline-block;
                padding: 4px 8px;
                background-color: #e6f4ea;
                color: #137333;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: 500;
            ">
                Disponible
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="
            padding: 20px; 
            border-radius: 8px; 
            background-color: white; 
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            height: 100%;
        ">
            <div style="font-size: 2rem; margin-bottom: 10px;">🔧</div>
            <h3>Maintenance Vectorielle</h3>
            <p>Maintenire et interrogez directement la base de données vectorielle.</p>
            <div style="
                display: inline-block;
                padding: 4px 8px;
                background-color: #e6f4ea;
                color: #137333;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: 500;
            ">
                Disponible
            </div>
        </div>
        """, unsafe_allow_html=True)
    
   
    
    # Carte de démarrage rapide
    st.markdown("""
    <h2 style="margin-top: 30px; margin-bottom: 20px;">Démarrage Rapide</h2>
    <div style="
        padding: 20px; 
        border-radius: 8px; 
        background-color: white; 
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    ">
        <h3>Comment utiliser l'Assistant Base de Données IA</h3>
        <ol>
            <li>Sélectionnez une fonctionnalité dans la navigation de la barre latérale</li>
            <li>Suivez les instructions pour chaque outil</li>
            <li>Pour l'Assistant BDD, posez des questions sur les bases de données ou SQL</li>
            <li>Consultez et utilisez les réponses générées dans votre système de base de données</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("Comment ça marche"):
        with st.container():
            st.markdown("""
                L'Assistant Base de Données IA utilise le traitement du langage naturel pour comprendre vos demandes et générer 
                des réponses adaptées aux bases de données :

                - **Assistant BDD** : Répond à vos questions sur les concepts de base de données et les bonnes pratiques
                - **Explorateur BDD Vectorielle** : Explore les documents stockés dans la base de données vectorielle

                Tout cela est alimenté par des modèles de langage avancés qui comprennent à la fois le langage naturel et les technologies de base de données.
            """)
            st.markdown("""
                <style>
                    div[data-testid="stContainer"] {
                        padding: 20px; 
                        border-radius: 8px; 
                        background-color: #f8f9fa;
                    }
                </style>
            """, unsafe_allow_html=True)