import streamlit as st
import time
import pandas as pd
from datetime import datetime
from utils.api import (
    list_knowledge_files, 
    backup_knowledge_files, 
    delete_knowledge_file, 
    delete_files_by_category,
    clear_vector_db,
    reindex_knowledge,
    clear_all_knowledge
)

def render_vector_db_cleanup_page():
    """Displays the vector database cleanup page."""
    st.title("Maintenance de la Base de Données Vectorielle")
    
    st.warning("""
    ⚠️ **Attention** : Les actions effectuées ici peuvent entraîner la perte de données.
    """)
    
    tab1, tab2, tab3 = st.tabs(["Fichiers de Connaissance", "Base Vectorielle", "Réinitialisation Complète"])
    
    with tab1:
        st.header("Gestion des Fichiers de Connaissance")
        
        if st.button("Actualiser la liste des fichiers"):
            st.cache_data.clear()
        
        with st.spinner("Chargement des fichiers..."):
            result = list_knowledge_files_cached()
        
        if "error" in result:
            st.error(f"Erreur: {result['error']}")
        else:
            files = result.get("files", [])
            
            if not files:
                st.info("Aucun fichier de connaissance trouvé.")
            else:
                df = pd.DataFrame(files)
                
                if not df.empty:
                    df["taille"] = df["size"].apply(format_file_size)
                    df["dernière_modification"] = df["modified"].apply(format_timestamp)
                    df["catégorie"] = df["category"]
                
                st.subheader("Statistiques")
                total_size = sum([f.get("size", 0) for f in files])
                category_counts = {}
                
                for f in files:
                    category = f.get("category", "unknown")
                    if category in category_counts:
                        category_counts[category] += 1
                    else:
                        category_counts[category] = 1
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Nombre total de fichiers", len(files))
                
                with col2:
                    st.metric("Taille totale", format_file_size(total_size))
                
                with col3:
                    categories_str = ", ".join([f"{k}: {v}" for k, v in category_counts.items()])
                    st.metric("Catégories", categories_str)
                
                st.subheader("Filtres")
                
                if category_counts:
                    category_options = ["Toutes"] + list(category_counts.keys())
                    selected_category = st.selectbox(
                        "Filtrer par catégorie", 
                        options=category_options
                    )
                else:
                    selected_category = "Toutes"
                
                filtered_df = df
                if selected_category != "Toutes":
                    filtered_df = df[df["catégorie"] == selected_category]
                
                if len(filtered_df) > 0:
                    st.subheader("Fichiers")
                    
                    display_df = filtered_df[["name", "catégorie", "taille", "dernière_modification"]]
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        column_config={
                            "name": "Nom du fichier",
                            "catégorie": "Catégorie",
                            "taille": "Taille",
                            "dernière_modification": "Dernière modification"
                        }
                    )
                    
                    st.subheader("Opérations sur les fichiers")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        selected_file = st.selectbox(
                            "Sélectionner un fichier à supprimer",
                            options=[f["path"] for f in files]
                        )
                        
                        if st.button("Supprimer le fichier sélectionné"):
                            if selected_file:
                                with st.spinner(f"Suppression de {selected_file}..."):
                                    result = delete_knowledge_file(selected_file)
                                
                                if "error" in result:
                                    st.error(f"Erreur: {result['error']}")
                                else:
                                    st.success(result.get("message", "Fichier supprimé avec succès"))
                                    time.sleep(1)
                                    st.rerun()
                    
                    with col2:
                        if category_counts:
                            category_to_delete = st.selectbox(
                                "Supprimer tous les fichiers d'une catégorie",
                                options=list(category_counts.keys())
                            )
                            
                            count_in_category = category_counts.get(category_to_delete, 0)
                            
                            if st.button(f"Supprimer tous les fichiers ({count_in_category}) de la catégorie {category_to_delete}"):
                                confirm = st.checkbox(
                                    f"Je confirme vouloir supprimer TOUS les fichiers de type '{category_to_delete}'",
                                    key="confirm_category_delete"
                                )
                                
                                if confirm:
                                    with st.spinner(f"Suppression des fichiers de catégorie {category_to_delete}..."):
                                        result = delete_files_by_category(category_to_delete)
                                    
                                    if "error" in result:
                                        st.error(f"Erreur: {result['error']}")
                                    else:
                                        st.success(result.get("message", "Fichiers supprimés avec succès"))
                                        time.sleep(1)
                                        st.rerun()
                    
                    st.subheader("Sauvegarde")
                    
                    if st.button("Créer une sauvegarde de tous les fichiers"):
                        with st.spinner("Création de la sauvegarde..."):
                            result = backup_knowledge_files()
                        
                        if "error" in result:
                            st.error(f"Erreur: {result['error']}")
                        else:
                            st.success(result.get("message", "Sauvegarde créée avec succès"))
    
    with tab2:
        st.header("Gestion de la Base de Données Vectorielle")
        
        st.subheader("Actions disponibles")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Vider la base vectorielle", use_container_width=True):
                with st.spinner("Nettoyage de la base vectorielle..."):
                    st.warning("""
                    ⚠️ Cette action va supprimer la base de données vectorielle actuelle.
                    Les fichiers de connaissance seront conservés, mais devront être réindexés.
                    """)
                    
                    confirm = st.checkbox(
                        "Je confirme vouloir vider la base vectorielle",
                        key="confirm_clear_db"
                    )
                    
                    if confirm:
                        result = clear_vector_db()
                        
                        if "error" in result:
                            st.error(f"Erreur: {result['error']}")
                        else:
                            st.success(result.get("message", "Base vectorielle vidée avec succès"))
        
        with col2:
            if st.button("Réindexer tous les fichiers", use_container_width=True):
                with st.spinner("Réindexation des fichiers..."):
                    st.info("""
                    Cette opération va reconstruire l'index de la base vectorielle à partir des fichiers existants.
                    Cela peut prendre un certain temps en fonction du volume de données.
                    """)
                    
                    result = reindex_knowledge()
                    
                    if "error" in result:
                        st.error(f"Erreur: {result['error']}")
                    else:
                        st.success(result.get("message", "Réindexation terminée avec succès"))
        
        st.subheader("Informations sur la base vectorielle")
        
        from utils.api import get_vector_db_stats
        
        with st.spinner("Chargement des statistiques..."):
            stats = get_vector_db_stats()
        
        if "error" in stats:
            st.warning("Impossible de récupérer les statistiques de la base vectorielle.")
            st.caption("La base de données vectorielle pourrait être vide ou pas encore initialisée.")
        else:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Documents indexés", stats.get("document_count", 0))
            
            with col2:
                st.metric("Dimensions des vecteurs", stats.get("embedding_dimensions", 0))
            
            with col3:
                st.metric("Longueur moyenne", f"{int(stats.get('average_document_length', 0))} caractères")
            
            sources = stats.get("sources", {})
            if sources:
                st.subheader("Distribution des sources")
                
                sources_df = pd.DataFrame({
                    "Source": list(sources.keys()),
                    "Nombre": list(sources.values())
                })
                
                if not sources_df.empty:
                    sources_df = sources_df.sort_values("Nombre", ascending=False)
                    
                    st.dataframe(
                        sources_df,
                        use_container_width=True,
                        column_config={
                            "Source": "Source",
                            "Nombre": "Nombre de documents"
                        }
                    )
        
        st.subheader("Recommandations de performance")
        st.info("""
        **Conseils pour optimiser les performances de la base vectorielle :**
        
        1. **Taille des chunks** : Des chunks trop grands ou trop petits peuvent affecter la qualité des résultats
        2. **Réindexation régulière** : Réindexez après l'ajout de nouveaux documents
        3. **Suppression des documents non pertinents** : Éliminez les fichiers qui ne sont plus utiles
        4. **Sauvegardes** : Effectuez régulièrement des sauvegardes avant les opérations de maintenance
        """)
    
    with tab3:
        st.header("Réinitialisation Complète du Système")
        
        st.error("""
        ⚠️ **ATTENTION : ZONE DANGEREUSE** ⚠️
        
        Cette opération va supprimer toutes les données du système et ne peut pas être annulée.
        """)
        
        st.warning("""
        Cette opération va :
        1. Créer une sauvegarde de tous les fichiers actuels
        2. Supprimer tous les fichiers de connaissance
        3. Vider la base de données vectorielle
        
        Après cette opération, le système sera vide et devra être réalimenté avec de nouveaux documents.
        """)
        
        reset_confirmation = st.checkbox("Je comprends que cette action est irréversible et je confirme vouloir réinitialiser tout le système")
        
        if reset_confirmation:
            if st.button("Réinitialiser le système", type="primary"):
                with st.spinner("Réinitialisation complète en cours..."):
                    backup_result = backup_knowledge_files()
                    if "error" in backup_result:
                        st.error(f"Erreur lors de la sauvegarde: {backup_result.get('error')}")
                    else:
                        # Continuer avec la réinitialisation
                        result = clear_all_knowledge()
                        
                        if "error" in result:
                            st.error(f"Erreur: {result['error']}")
                        else:
                            st.success(f"Système réinitialisé avec succès. Une sauvegarde a été créée: {backup_result.get('message', '')}")
                            time.sleep(2)
                            st.rerun()
        
        debug_expander = st.expander("Informations de diagnostic")
        
        with debug_expander:
            st.markdown("""
            ### Chemins des répertoires
            
            - **Knowledge**: `./knowledge`
            - **Base vectorielle**: `./database/vector_db`
            - **Sauvegardes**: `./database/backups`
            
            ### Diagnostic
            
            Vous pouvez exécuter les commandes suivantes dans un terminal pour diagnostiquer les problèmes :
            
            ```bash
            # Vérifier les fichiers de connaissance
            ls -la ./knowledge
            
            # Vérifier la base vectorielle
            ls -la ./database/vector_db
            
            # Vérifier les sauvegardes
            ls -la ./database/backups
            ```
            """)
            
            if st.button("Afficher tous les détails des fichiers"):
                result = list_knowledge_files_cached()
                
                if "error" not in result:
                    files = result.get("files", [])
                    if files:
                        st.json(files)
                    else:
                        st.info("Aucun fichier trouvé.")
                else:
                    st.error(f"Erreur: {result['error']}")

def format_file_size(size_in_bytes):
    """Format file size to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} TB"

def format_timestamp(timestamp):
    """Format timestamp to human-readable format."""
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Date inconnue"

@st.cache_data(ttl=300)
def list_knowledge_files_cached():
    """Cached version of list_knowledge_files."""
    return list_knowledge_files()