import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import io
import os
from utils.api import (
    get_vector_db_stats, 
    get_vector_db_documents, 
    get_vector_db_document,
    search_vector_db,
    upload_knowledge_document
)

def render_vector_db_explorer_page():
    """Affiche la page d'explorateur de base de données vectorielle."""
    st.title("Explorateur de Base de Données Vectorielle")
    
    tab1, tab2, tab3 = st.tabs(["Aperçu", "Explorateur de Documents", "Recherche"])
    
    with tab1:
        st.header("Aperçu de la Base de Données Vectorielle")
        
        if st.button("Actualiser les statistiques"):
            st.cache_data.clear()
        
        stats = get_vector_db_stats_cached()
        
        if "error" in stats:
            st.error(f"Erreur lors de la récupération des statistiques : {stats['error']}")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total des Documents", stats.get("document_count", 0))
                st.metric("Dimensions des Embeddings", stats.get("embedding_dimensions", 0))
            
            with col2:
                st.metric("Longueur Moyenne des Documents", f"{int(stats.get('average_document_length', 0))} caractères")
                st.metric("Nombre de Sources", len(stats.get("sources", {})))
            
            if stats.get("sources"):
                st.subheader("Sources des Documents")
                
                sources_df = pd.DataFrame({
                    "Source": list(stats["sources"].keys()),
                    "Nombre": list(stats["sources"].values())
                })
                
                sources_df = sources_df.sort_values("Nombre", ascending=False)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.pie(sources_df["Nombre"], labels=sources_df["Source"], autopct='%1.1f%%')
                ax.axis('equal')
                st.pyplot(fig)
                
                st.dataframe(sources_df)
        
        st.subheader("Télécharger un Nouveau Document")
        
        accepted_formats = ["txt", "pdf", "docx", "md", "csv", "json", "xml", "html"]
        
        # UPDATED: Enhanced format information with OCR capabilities
        with st.expander("Formats de fichiers supportés"):
            st.markdown("""
            L'indexation vectorielle peut traiter les formats suivants :
            - **Texte brut** (.txt)
            - **Documents structurés** (.pdf, .docx) 
              - ✨ *Extraction automatique du texte des images incluses via OCR*
            - **Données structurées** (.csv, .json, .xml)
            - **Contenu web** (.html)
            - **Documentation** (.md)
            
            **🔍 Nouvelle fonctionnalité OCR :**
            - Les PDFs et documents Word contenant des images avec du texte seront automatiquement traités
            - Le texte des images sera extrait et indexé avec le reste du document
            - Ceci inclut les diagrammes, screenshots, schémas de base de données, et images scannées
            - Prend en charge plusieurs langues (anglais, français, etc.)
            
            Note : Les fichiers avec images peuvent prendre plus de temps à indexer en raison du traitement OCR.
            """)
        
        uploaded_file = st.file_uploader(
            "Choisissez un fichier à indexer", 
            type=accepted_formats,
            help="Téléchargez un fichier pour l'ajouter à la base de connaissances vectorielle"
        )
        
        if uploaded_file is not None:
            file_details = {
                "Nom du fichier": uploaded_file.name,
                "Type de fichier": uploaded_file.type,
                "Taille": f"{uploaded_file.size / 1024:.2f} KB"
            }
            
            st.write("Détails du fichier :")
            for k, v in file_details.items():
                st.write(f"- **{k}:** {v}")
            
            # UPDATED: Check if file might contain images for OCR processing
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            might_have_images = file_extension in ['.pdf', '.docx', '.doc']
            
            # UPDATED: Show OCR information if applicable
            if might_have_images:
                st.info("📷 Ce type de fichier peut contenir des images. Si c'est le cas, le texte sera automatiquement extrait via OCR.")
            
            if uploaded_file.type.startswith("text/") or uploaded_file.name.endswith(".txt"):
                if st.checkbox("Prévisualiser le contenu"):
                    content = uploaded_file.getvalue().decode("utf-8")
                    st.text_area("Aperçu du contenu", value=content[:1000] + ("..." if len(content) > 1000 else ""), height=200)
            
            # UPDATED: Enhanced upload button with OCR status
            if st.button("Télécharger et Indexer le Document"):
                # Show different spinner message based on file type
                spinner_message = f"Téléchargement et indexation de {uploaded_file.name}..."
                if might_have_images:
                    spinner_message += " (incluant traitement OCR des images)"
                
                with st.spinner(spinner_message):
                    result = upload_knowledge_document(uploaded_file)
                
                if "error" in result:
                    st.error(f"Erreur lors du téléchargement du document : {result['error']}")
                else:
                    message = result.get("message", "Document téléchargé avec succès")
                    
                    # UPDATED: Enhanced success message with OCR status
                    if "incluant l'extraction de texte des images" in message:
                        st.success("✅ " + message)
                        st.info("🔍 Du texte a été trouvé et extrait des images dans votre document ! Vous pouvez maintenant rechercher ce contenu.")
                        
                        # Show additional info about OCR processing
                        with st.expander("ℹ️ Détails du traitement OCR"):
                            st.markdown("""
                            **Traitement effectué :**
                            - ✅ Images extraites du document
                            - ✅ Texte reconnu via OCR (Optical Character Recognition)
                            - ✅ Contenu indexé dans la base de données vectorielle
                            - ✅ Prêt pour la recherche et les questions
                            
                            Vous pouvez maintenant utiliser l'**Assistant Base de Données** pour poser des questions 
                            sur le contenu textuel ET sur le texte extrait des images !
                            """)
                    else:
                        st.success("✅ " + message)
                        if might_have_images:
                            st.info("ℹ️ Aucune image avec du texte lisible détectée dans ce document.")
                    
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()
    
    with tab2:
        st.header("Explorateur de Documents")
        
        page_size = 10
        current_page = st.session_state.get("current_page", 1)
        
        offset = (current_page - 1) * page_size
        
        docs_result = get_vector_db_documents_cached(limit=page_size, offset=offset)
        
        if "error" in docs_result:
            st.error(f"Erreur lors de la récupération des documents : {docs_result['error']}")
        else:
            documents = docs_result.get("documents", [])
            total_docs = docs_result.get("total", 0)
            total_pages = (total_docs + page_size - 1) // page_size if total_docs > 0 else 1
            
            col1, col2, col3, col4 = st.columns([1, 3, 3, 1])
            
            with col1:
                if current_page > 1:
                    if st.button("←"):
                        st.session_state.current_page = current_page - 1
                        st.rerun()
            
            with col2:
                st.write(f"Page {current_page} sur {total_pages}")
            
            with col3:
                page_input = st.number_input(
                    "Aller à la page", 
                    min_value=1, 
                    max_value=max(1, total_pages),
                    value=current_page,
                    label_visibility="collapsed"
                )
                
                if page_input != current_page:
                    st.session_state.current_page = page_input
                    st.rerun()
            
            with col4:
                if current_page < total_pages:
                    if st.button("→"):
                        st.session_state.current_page = current_page + 1
                        st.rerun()
            
            if documents:
                for doc in documents:
                    # UPDATED: Enhanced document display with OCR indicator
                    doc_metadata = doc.get("metadata", {})
                    doc_title = doc.get('id', 'Inconnu')
                    
                    # Check if this is an OCR-extracted document
                    is_ocr_content = doc_metadata.get("type") == "ocr_extracted"
                    
                    if is_ocr_content:
                        doc_title = f"📷 OCR: {doc_metadata.get('original_file', 'Image extraite')}"
                    
                    with st.expander(f"Document : {doc_title}"):
                        # UPDATED: Show OCR indicator in metadata
                        if is_ocr_content:
                            st.warning("🔍 Ce contenu a été extrait d'images via OCR")
                        
                        st.markdown("#### Métadonnées")
                        
                        for key, value in doc_metadata.items():
                            # Make OCR-specific metadata more readable
                            if key == "type" and value == "ocr_extracted":
                                st.write(f"**Type:** Texte extrait d'images (OCR)")
                            elif key == "original_file":
                                st.write(f"**Fichier source:** {value}")
                            else:
                                st.write(f"**{key}:** {value}")
                        
                        st.markdown("#### Contenu")
                        content = doc.get("content", "Aucun contenu disponible")
                        
                        # Show preview for OCR content
                        if is_ocr_content and content.startswith("=== EXTRACTED TEXT FROM IMAGES ==="):
                            content = content.replace("=== EXTRACTED TEXT FROM IMAGES ===", "").strip()
                            st.info("📝 Aperçu du texte extrait des images :")
                        
                        st.text_area(
                            "Contenu du document",
                            value=content,
                            height=200,
                            label_visibility="collapsed"
                        )
            else:
                st.info("Aucun document trouvé dans la base de données vectorielle.")
    
    with tab3:
        st.header("Rechercher dans la Base de Données Vectorielle")
        
        # UPDATED: Add information about OCR content in search
        st.markdown("""
        🔍 **Recherche intelligente** : Cette recherche inclut maintenant le contenu extrait des images 
        via OCR (diagrammes, schémas, texte scanné, etc.) en plus du texte traditionnel.
        """)
        
        query = st.text_input("Entrez votre requête de recherche :")
        k = st.slider("Nombre de résultats :", min_value=1, max_value=20, value=5)
        
        if st.button("Rechercher") and query:
            with st.spinner("Recherche en cours..."):
                results = search_vector_db(query, k)
            
            if "error" in results:
                st.error(f"Erreur lors de la recherche : {results['error']}")
            else:
                search_results = results.get("results", [])
                
                if not search_results:
                    st.info("Aucun document correspondant trouvé.")
                else:
                    for i, result in enumerate(search_results):
                        similarity = result.get("similarity_score", 0)
                        similarity_percentage = (1 - similarity) * 100
                        
                        # UPDATED: Check if result is from OCR content
                        metadata = result.get("metadata", {})
                        is_ocr_result = metadata.get("type") == "ocr_extracted"
                        
                        result_title = f"Résultat {i+1} - Similarité : {similarity_percentage:.2f}%"
                        if is_ocr_result:
                            result_title += " 📷 (Contenu OCR)"
                        
                        with st.expander(result_title):
                            # UPDATED: Show OCR indicator for search results
                            if is_ocr_result:
                                st.success("🔍 Ce résultat provient du texte extrait d'images via OCR")
                            
                            st.markdown("#### Métadonnées")
                            
                            for key, value in metadata.items():
                                if key == "type" and value == "ocr_extracted":
                                    st.write(f"**Type:** Texte extrait d'images (OCR)")
                                elif key == "original_file":
                                    st.write(f"**Fichier source:** {value}")
                                else:
                                    st.write(f"**{key}:** {value}")
                            
                            st.markdown("#### Contenu")
                            content = result.get("content", "Aucun contenu disponible")
                            
                            # Clean up OCR content display
                            if is_ocr_result and content.startswith("=== EXTRACTED TEXT FROM IMAGES ==="):
                                content = content.replace("=== EXTRACTED TEXT FROM IMAGES ===", "").strip()
                            
                            st.text_area(
                                f"Contenu du document {i}",
                                value=content,
                                height=200,
                                label_visibility="collapsed"
                            )

@st.cache_data(ttl=300)
def get_vector_db_stats_cached():
    """Version mise en cache de get_vector_db_stats."""
    return get_vector_db_stats()

@st.cache_data(ttl=300)
def get_vector_db_documents_cached(limit=10, offset=0):
    """Version mise en cache de get_vector_db_documents."""
    return get_vector_db_documents(limit, offset)