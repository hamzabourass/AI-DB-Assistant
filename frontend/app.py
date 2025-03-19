import streamlit as st
from modules.home import render_home_page
from modules.sql_generator import render_sql_generator_page
from modules.db_knowledge import render_db_knowledge_page
from modules.vector_db_explorer import render_vector_db_explorer_page
from modules.sqlite_db_explorer import render_sqlite_db_explorer_page
from utils.api import check_api_status
from utils.styles import load_css
from modules.video_transcription import render_video_transcription_page

# Configuration de la page
st.set_page_config(
    page_title="Assistant BDD IA",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chargement du CSS personnalisé
load_css()

# Définition des options de navigation avec des icônes
PAGES = {
    "🏠  Accueil": "Accueil",
    "💬  Assistant Base de Données": "Assistant Base de Données",
    "🔍  Explorateur BDD Vectorielle": "Explorateur de Base Vectorielle",
    "🎥  Transcription Vidéo": "Transcription Vidéo",  # Add this line
}
# Configuration de la barre latérale
def render_sidebar():
    with st.sidebar:
        st.title("Assistant BDD IA")
        
        # Navigation
        st.markdown("### Navigation")
        
        # Initialisation de la page active dans le state de session
        if 'active_page' not in st.session_state:
            st.session_state.active_page = "Accueil"
        
        # Création d'une liste de boutons radio qui ressemblent à une liste de navigation
        selected_page_label = [k for k, v in PAGES.items() if v == st.session_state.active_page][0]
        
        selected_option = st.radio(
            label="Navigation",
            options=list(PAGES.keys()),
            index=list(PAGES.keys()).index(selected_page_label),
            label_visibility="collapsed"
        )
        
        # Mise à jour de la page active si changée
        if PAGES[selected_option] != st.session_state.active_page:
            st.session_state.active_page = PAGES[selected_option]
            st.rerun()
        
        st.divider()
        
        # Statut API
        api_status = check_api_status()
        if api_status["connected"]:
            st.success("✅ API Connectée", icon="✅")
        else:
            st.error("❌ API Déconnectée", icon="❌")
        
        st.caption("Version 0.4")
    
    return st.session_state.active_page

# Application principale
def main():
    selected_page = render_sidebar()

    if selected_page == "Accueil":
        render_home_page()
    elif selected_page == "Assistant Base de Données":
        render_db_knowledge_page()
    elif selected_page == "Explorateur de Base Vectorielle":
        render_vector_db_explorer_page()
    elif selected_page == "Transcription Vidéo":
       render_video_transcription_page()


if __name__ == "__main__":
    main()