import streamlit as st
from utils.api import answer_db_question, save_chat, get_chat, list_chats, delete_chat, create_new_chat
import time
import uuid

def render_db_knowledge_page():
    """Render the Database Knowledge page with Streamlit's built-in chat components."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())

    st.title("Database Knowledge")

    # Display debug info in sidebar if checked
    if st.sidebar.checkbox("Show Debug Info", False):
        st.sidebar.write(f"Conversation ID: {st.session_state.conversation_id}")
        st.sidebar.write(f"Message Count: {len(st.session_state.chat_history)}")
        if st.sidebar.button("🗑️ Clear Conversation"):
            st.session_state.chat_history = []
            st.session_state.conversation_id = str(uuid.uuid4())
            st.rerun()

    # Display chat messages from history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

    # Display example questions if no chat history
    if not st.session_state.chat_history:
        # st.info("### Database Knowledge Assistant")
        st.write("Ask questions about database concepts, SQL syntax, and optimization techniques.")
        # st.write("The assistant maintains context between questions, so you can ask follow-up questions.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("What is database normalization?", use_container_width=True):
                process_question("What is database normalization?")
                st.rerun()
        with col2:
            if st.button("How to use indexes?", use_container_width=True):
                process_question("How to use indexes?")
                st.rerun()
        with col3:
            if st.button("Explain JOIN types", use_container_width=True):
                process_question("Explain JOIN types")
                st.rerun()

    # Chat input
    if prompt := st.chat_input("Ask a question about databases:"):
        process_question(prompt)
        st.rerun()

def process_question(question):
    """Process a user question and add to chat history."""
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": question})
    
    # Display user message immediately
    with st.chat_message("user"):
        st.write(question)
    
    # Display assistant response with thinking indicator
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.info("Thinking...")
        
        # Get response from backend
        result = answer_db_question(
            question, 
            st.session_state.conversation_id
        )
        
        if result["success"]:
            # Update chat history with bot response
            response = result["answer"]
            st.session_state.chat_history.append({
                "role": "bot", 
                "content": response
            })
            
            # Display final response
            message_placeholder.write(response)
            
            # Update conversation ID if provided
            if "conversation_id" in result and result["conversation_id"]:
                st.session_state.conversation_id = result["conversation_id"]
                
            # Save chat history
            try:
                save_chat(
                    st.session_state.conversation_id,
                    st.session_state.chat_history,
                    st.session_state.chat_history[0]["content"] if st.session_state.chat_history else "New Conversation"
                )
            except Exception as e:
                print(f"Error saving chat: {e}")
        else:
            # Handle error
            error_message = f"Sorry, I couldn't process your question. {result.get('error', '')} {result.get('message', '')}"
            st.session_state.chat_history.append({
                "role": "bot", 
                "content": error_message
            })
            message_placeholder.error(error_message)