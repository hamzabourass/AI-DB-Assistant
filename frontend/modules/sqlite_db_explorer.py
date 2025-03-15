# modules/sqlite_db_explorer.py
import streamlit as st
import sqlite3
import pandas as pd
import os
import sys
import json
from pathlib import Path

def render_sqlite_db_explorer_page():
    """Affiche une page pour explorer la base de données SQLite."""
    st.title("Explorateur de Base de Données SQLite")
    
    # Chemin vers la base de données - ajusté pour le dossier backend
    # Récupération du répertoire actuel (frontend)
    current_dir = Path.cwd()
    # Navigation vers le répertoire parent puis vers backend/database
    backend_dir = current_dir.parent / "backend"
    db_path = backend_dir / "database" / "history.db"
    
    # Vérification de l'existence de la base de données
    if not db_path.exists():
        st.error(f"Fichier de base de données introuvable à : {db_path}")
        st.info("Veuillez vérifier le chemin de la base de données dans le code si vous êtes sûr que la base de données existe.")
        
        # Informations de débogage
        with st.expander("Infos de débogage"):
            st.write("Répertoire actuel :", current_dir)
            st.write("Répertoire backend attendu :", backend_dir)
            st.write("Chemin de base de données attendu :", db_path)
            st.write("Contenu du répertoire parent :", [str(p) for p in current_dir.parent.iterdir()])
            if backend_dir.exists():
                st.write("Contenu du répertoire backend :", [str(p) for p in backend_dir.iterdir()])
                db_dir = backend_dir / "database"
                if db_dir.exists():
                    st.write("Contenu du répertoire database :", [str(p) for p in db_dir.iterdir()])
        
        # Saisie de chemin personnalisé
        custom_path = st.text_input(
            "Entrez un chemin de base de données personnalisé :",
            value=str(db_path)
        )
        
        if st.button("Essayer le chemin personnalisé"):
            db_path = Path(custom_path)
            if not db_path.exists():
                st.error(f"Base de données toujours introuvable à : {custom_path}")
                return
            st.success(f"Base de données trouvée à : {custom_path}")
        else:
            return
    
    try:
        # Connexion à la base de données SQLite
        conn = sqlite3.connect(db_path)
        
        # Récupération de la liste des tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            st.warning("Aucune table trouvée dans la base de données.")
            return
            
        # Formatage des noms de tables pour la sélection
        table_names = [table[0] for table in tables]
        
        # Infos de la base de données
        st.success(f"Connecté à la base de données : {db_path}")
        st.write(f"Trouvé {len(table_names)} tables")
        
        # Sélection de la table à afficher
        selected_table = st.selectbox("Sélectionnez une table à afficher :", table_names)
        
        if selected_table:
            # Récupération des informations de la table
            cursor.execute(f"PRAGMA table_info({selected_table})")
            columns_info = cursor.fetchall()
            
            # Affichage du schéma de la table
            with st.expander("Schéma de la table", expanded=False):
                schema_df = pd.DataFrame(columns_info, 
                                         columns=['cid', 'name', 'type', 'notnull', 'default_value', 'pk'])
                st.dataframe(schema_df)
            
            # Récupération du nombre de lignes
            cursor.execute(f"SELECT COUNT(*) FROM {selected_table}")
            row_count = cursor.fetchone()[0]
            st.write(f"Nombre total de lignes : {row_count}")
            
            # Options de requête
            st.subheader("Options de requête")
            
            # Récupération des noms de colonnes
            column_names = [col[1] for col in columns_info]
            
            # Option pour sélectionner des colonnes spécifiques
            selected_columns = st.multiselect(
                "Sélectionnez les colonnes à afficher (laissez vide pour toutes) :",
                options=column_names,
                default=[]
            )
            
            # Options de filtrage
            with st.expander("Options de filtrage", expanded=False):
                filter_column = st.selectbox(
                    "Filtrer par colonne :",
                    options=["Aucune"] + column_names
                )
                
                filter_value = None
                if filter_column != "Aucune":
                    filter_value = st.text_input("Valeur de filtre :")
            
            # Option de limitation des résultats
            limit = st.number_input("Limiter le nombre de lignes :", min_value=1, max_value=1000, value=100)
            
            # Bouton d'exécution de la requête
            if st.button("Exécuter la requête"):
                # Construction de la requête SQL
                columns_str = ", ".join(selected_columns) if selected_columns else "*"
                query = f"SELECT {columns_str} FROM {selected_table}"
                
                # Ajout de la clause WHERE si un filtre est appliqué
                if filter_column != "Aucune" and filter_value:
                    query += f" WHERE {filter_column} LIKE '%{filter_value}%'"
                
                # Ajout de la clause LIMIT
                query += f" LIMIT {limit}"
                
                # Exécution et affichage des résultats
                results = pd.read_sql_query(query, conn)
                
                st.subheader("Résultats de la requête")
                st.code(query, language="sql")
                
                if results.empty:
                    st.info("Aucun résultat trouvé.")
                else:
                    st.dataframe(results, use_container_width=True)
                    
                    # Option de téléchargement
                    csv = results.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Télécharger en CSV",
                        csv,
                        f"{selected_table}_export.csv",
                        "text/csv",
                        key='download-csv'
                    )
            
            # Option pour requête SQL personnalisée
            st.subheader("Requête SQL personnalisée")
            custom_query = st.text_area(
                "Entrez une requête SQL personnalisée :",
                value=f"SELECT * FROM {selected_table} LIMIT 10;"
            )
            
            if st.button("Exécuter la requête personnalisée"):
                try:
                    custom_results = pd.read_sql_query(custom_query, conn)
                    
                    if custom_results.empty:
                        st.info("Aucun résultat trouvé.")
                    else:
                        st.dataframe(custom_results, use_container_width=True)
                        
                        # Option de téléchargement pour la requête personnalisée
                        custom_csv = custom_results.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "Télécharger les résultats de la requête personnalisée",
                            custom_csv,
                            "requete_personnalisee_export.csv",
                            "text/csv",
                            key='download-custom-csv'
                        )
                except Exception as e:
                    st.error(f"Erreur lors de l'exécution de la requête : {str(e)}")
        
        # Fermeture de la connexion
        conn.close()
        
    except sqlite3.Error as e:
        st.error(f"Erreur de base de données : {str(e)}")
    except Exception as e:
        st.error(f"Une erreur s'est produite : {str(e)}")