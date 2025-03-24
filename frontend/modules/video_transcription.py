import streamlit as st
import time
from datetime import datetime
from utils.api import upload_video_for_transcription, list_transcriptions, get_transcription

def render_video_transcription_page():
    """Displays the video transcription page."""
    st.title("Transcription de Vidéos et audio")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Télécharger", "Liste des Transcriptions", "Recherche"])
    
    # Upload tab
    with tab1:
        st.header("Télécharger une vidéo ou un audio pour transcription")
        
        # Model selection
        model_size = st.selectbox(
            "Modèle de transcription",
            options=["tiny", "base", "small", "medium", "large"],
            index=1,  # Default to "base"
            help="Les modèles plus grands sont plus précis mais plus lents et demandent plus de ressources."
        )
        
        uploaded_file = st.file_uploader(
            "Choisissez un fichier vidéo ou audio",
            type=["mp4", "avi", "mov", "mkv", "webm", "mp3", "wav", "ogg", "m4a"],
            help="Formats supportés: Vidéo (MP4, AVI, MOV, MKV, WebM) ou Audio (MP3, WAV, OGG, M4A)"
        )
        
        if uploaded_file is not None:
            # Display file info
            file_details = {
                "Nom du fichier": uploaded_file.name,
                "Type de fichier": uploaded_file.type,
                "Taille": f"{uploaded_file.size / (1024 * 1024):.2f} MB"
            }
            
            st.write("Détails du fichier:")
            for k, v in file_details.items():
                st.write(f"- **{k}:** {v}")
            
            # Process button
            if st.button("Transcription et indexation"):
                with st.spinner("Traitement de la vidéo en cours... Cette opération peut prendre plusieurs minutes."):
                    try:
                        # Call the API to upload and transcribe the video
                        result = upload_video_for_transcription(uploaded_file, model_size)
                        
                        if "error" in result:
                            st.error(f"Erreur: {result['error']}")
                        else:
                            st.success("Vidéo traitée avec succès!")
                            st.json(result)
                            
                            # Clear the file uploader
                            st.session_state.file_uploader_key = None
                            
                            # Wait a moment to let the reindexing finish
                            time.sleep(2)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Erreur lors du traitement: {str(e)}")
        
        # Display information about usage
        with st.expander("Comment ça marche?"):
            st.markdown("""
            ### Processus de transcription
            
            1. **Téléchargement**: Votre vidéo ou audio est téléchargée vers le serveur
            2. **Extraction audio**: L'audio est extrait de la vidéo si c'est video
            3. **Transcription**: Le modèle Whisper transcrit l'audio en texte
            4. **Indexation**: La transcription est ajoutée à la base de connaissances vectorielle
            5. **RAG**: La transcription peut maintenant être utilisée pour répondre à vos questions
            
            ### Choix du modèle
            
            - **tiny**: Rapide mais moins précis (1GB VRAM)
            - **base**: Bon équilibre vitesse/précision (1GB VRAM)
            - **small**: Plus précis, plus lent (2GB VRAM)
            - **medium**: Haute précision, lent (5GB VRAM)
            - **large**: La plus haute précision, très lent (10GB VRAM)
            """)
    
    # List tab
    with tab2:
        st.header("Transcriptions disponibles")
        
        if st.button("Actualiser"):
            st.cache_data.clear()
        
        try:
            result = list_transcriptions_cached()
            
            if "error" in result:
                st.error(f"Erreur: {result['error']}")
            else:
                transcriptions = result.get("transcriptions", [])
                
                if not transcriptions:
                    st.info("Aucune transcription disponible. Téléchargez une vidéo pour commencer.")
                else:
                    # Sort by most recent first
                    transcriptions.sort(key=lambda x: x.get("modified", 0), reverse=True)
                    
                    for idx, trans in enumerate(transcriptions):
                        with st.expander(f"{trans.get('video_name', 'Vidéo')} ({format_timestamp(trans.get('modified', 0))})"):
                            # Display metadata
                            st.write(f"**Taille du fichier:** {trans.get('size', 0) / 1024:.2f} KB")
                            st.write(f"**Créé le:** {format_timestamp(trans.get('created', 0))}")
                            st.write(f"**Modifié le:** {format_timestamp(trans.get('modified', 0))}")
                            
                            # Get and display content
                            trans_id = trans.get('video_name', '')
                            if trans_id:
                                content_result = get_transcription_cached(trans_id)
                                if "error" not in content_result:
                                    st.markdown("### Contenu")
                                    st.text_area(
                                        "Transcription",
                                        value=content_result.get("content", ""),
                                        height=200,
                                        label_visibility="collapsed"
                                    )
                                    
                                    # Button to search this transcription in the vector DB
                                    if st.button("Rechercher dans cette transcription", key=f"search_{idx}"):
                                        # Store the transcription ID in session state
                                        st.session_state.search_transcription = trans_id
                                        # Switch to search tab
                                        st.session_state.active_tab = "Recherche"
                                        st.rerun()
                                else:
                                    st.error(f"Erreur lors de la récupération du contenu: {content_result.get('error')}")
        except Exception as e:
            st.error(f"Erreur lors de la récupération des transcriptions: {str(e)}")
    
    # Search tab
    with tab3:
        st.header("Recherche dans les transcriptions")
        
        # Connect to the vector DB explorer
        st.markdown("""
        Les transcriptions sont indexées dans la base de connaissances vectorielle.
        
        Utilisez l'**Explorateur de Base Vectorielle** depuis le menu principal pour rechercher
        dans toutes vos transcriptions et autres documents.
        
        Vous pouvez également utiliser l'**Assistant Base de Données** pour poser des questions
        dont les réponses peuvent se trouver dans vos transcriptions vidéo.
        """)
        
        # Link to those pages
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Aller à l'Explorateur Vectoriel", use_container_width=True):
                st.session_state.active_page = "Explorateur de Base Vectorielle"
                st.rerun()
        with col2:
            if st.button("Aller à l'Assistant BDD", use_container_width=True):
                st.session_state.active_page = "Assistant Base de Données"
                st.rerun()

def format_timestamp(timestamp):
    """Format a timestamp to a readable date."""
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Date inconnue"

@st.cache_data(ttl=300)
def list_transcriptions_cached():
    """Cached version of list_transcriptions."""
    return list_transcriptions()

@st.cache_data(ttl=300)
def get_transcription_cached(transcription_id):
    """Cached version of get_transcription."""
    return get_transcription(transcription_id)