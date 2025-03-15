import streamlit as st
from utils.api import answer_db_question, save_chat, get_chat, list_chats, delete_chat, create_new_chat
import time
import uuid

def render_db_knowledge_page():
    """Affiche la page d'assistant base de données avec les composants de chat Streamlit."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())

    st.title("Assistant Base de Données")

    # Affichage des informations de débogage dans la barre latérale si coché
    if st.sidebar.checkbox("Afficher les infos de débogage", False):
        st.sidebar.write(f"ID de conversation : {st.session_state.conversation_id}")
        st.sidebar.write(f"Nombre de messages : {len(st.session_state.chat_history)}")
        if st.sidebar.button("🗑️ Effacer la conversation"):
            st.session_state.chat_history = []
            st.session_state.conversation_id = str(uuid.uuid4())
            st.rerun()

    # Affichage des messages du chat à partir de l'historique
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

    # Affichage des questions d'exemple si l'historique est vide
    if not st.session_state.chat_history:
        st.write("Posez des questions sur les concepts de base de données, la syntaxe SQL et les techniques d'optimisation.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Qu'est-ce que la normalisation de base de données ?", use_container_width=True):
                process_question("Qu'est-ce que la normalisation de base de données ?")
                st.rerun()
        with col2:
            if st.button("Comment utiliser les index ?", use_container_width=True):
                process_question("Comment utiliser les index ?")
                st.rerun()
        with col3:
            if st.button("Expliquer les types de JOIN", use_container_width=True):
                process_question("Expliquer les types de JOIN")
                st.rerun()

    # Saisie du chat
    if prompt := st.chat_input("Posez une question sur les bases de données :"):
        process_question(prompt)
        st.rerun()

def process_question(question):
    """Traite une question utilisateur et l'ajoute à l'historique du chat."""
    # Ajout du message utilisateur à l'historique
    st.session_state.chat_history.append({"role": "user", "content": question})
    
    # Affichage immédiat du message utilisateur
    with st.chat_message("user"):
        st.write(question)
    
    # Affichage de la réponse de l'assistant avec indicateur de réflexion
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.info("En train de réfléchir...")
        
        # Obtention de la réponse du backend, en passant l'historique du chat actuel
        result = answer_db_question(
            question, 
            st.session_state.conversation_id,
            st.session_state.chat_history
        )
        
        if result["success"]:
            # Mise à jour de l'historique avec la réponse du bot
            response = result["answer"]
            st.session_state.chat_history.append({
                "role": "bot", 
                "content": response
            })
            
            # Affichage de la réponse finale
            message_placeholder.write(response)
            
            # Mise à jour de l'ID de conversation si fourni
            if "conversation_id" in result and result["conversation_id"]:
                st.session_state.conversation_id = result["conversation_id"]
                
            # Sauvegarde de l'historique du chat
            try:
                save_chat(
                    st.session_state.conversation_id,
                    st.session_state.chat_history,
                    st.session_state.chat_history[0]["content"] if st.session_state.chat_history else "Nouvelle Conversation"
                )
            except Exception as e:
                print(f"Erreur lors de la sauvegarde du chat: {e}")
        else:
            # Gestion des erreurs
            error_message = f"Désolé, je n'ai pas pu traiter votre question. {result.get('error', '')} {result.get('message', '')}"
            st.session_state.chat_history.append({
                "role": "bot", 
                "content": error_message
            })
            message_placeholder.error(error_message)