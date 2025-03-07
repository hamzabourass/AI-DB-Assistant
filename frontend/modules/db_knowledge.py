import streamlit as st
from utils.api import answer_db_question, save_chat, get_chat, list_chats, delete_chat, create_new_chat
import time
import uuid

def render_db_knowledge_page():
    """Render the Database Knowledge page with a chat-like interface."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())

    st.markdown("""
    <style>
    .chat-message {
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        max-width: 80%;
        word-wrap: break-word;
    }
    .user-message {
        background: #f1f0f0;
        margin-left: auto;
    }
    .bot-message {
        background: #e3f2fd;
        margin-right: auto;
    }
    .question-chip {
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        border-radius: 20px;
        background: #f0f2f6;
        cursor: pointer;
        transition: 0.3s;
    }
    .question-chip:hover {
        background: #e2e5e9;
    }
    .stTextInput>div>input {
        padding: 1rem 1.5rem !important;
        border-radius: 25px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display: flex; align-items: center; gap: 1rem;">
        <h1 class='main-header'>Database Knowledge</h1>
    </div>
    """, unsafe_allow_html=True)

    chat_container = st.container()

    if st.sidebar.checkbox("Show Debug Info", False):
        st.sidebar.write(f"Conversation ID: {st.session_state.conversation_id}")
        st.sidebar.write(f"Message Count: {len(st.session_state.chat_history)}")
        if st.button("🗑️ Clear Conversation"):
            st.session_state.chat_history = []
            st.session_state.conversation_id = str(uuid.uuid4())
            st.rerun()

    with st.form("chat_input", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        with col1:
            user_input = st.text_input(
                "Ask a question about databases:",
                placeholder="Type your question here...",
                label_visibility="collapsed",
                key="input_text"
            )
        with col2:
            submitted = st.form_submit_button("➤", use_container_width=True)

        if submitted and user_input:
            process_question(user_input)
            st.rerun()

    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(
                    f"<div class='chat-message user-message'>{msg['content']}</div>", 
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"<div class='chat-message bot-message'>{msg['content']}</div>", 
                    unsafe_allow_html=True
                )

        if not st.session_state.chat_history:
            st.markdown("""
            <div style="text-align: center; padding: 2rem 0; color: #666;">
                <h3>Database Knowledge Assistant</h3>
                <p>Ask questions about database concepts, SQL syntax, and optimization techniques.</p>
                <p>The assistant maintains context between questions, so you can ask follow-up questions.</p>
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center;">
                    <div class="question-chip">What is database normalization?</div>
                    <div class="question-chip">How to use indexes?</div>
                    <div class="question-chip">Explain JOIN types</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def process_question(question):
    """Process a user question and add to chat history."""
    st.session_state.chat_history.append({"role": "user", "content": question})
    
    with st.spinner("Thinking..."):
        result = answer_db_question(
            question, 
            st.session_state.conversation_id
        )
        
        if result["success"]:
            st.session_state.chat_history.append({
                "role": "bot", 
                "content": result["answer"]
            })
            
            if "conversation_id" in result and result["conversation_id"]:
                st.session_state.conversation_id = result["conversation_id"]
                
            try:
                save_chat(
                    st.session_state.conversation_id,
                    st.session_state.chat_history,
                    st.session_state.chat_history[0]["content"] if st.session_state.chat_history else "New Conversation"
                )
            except Exception as e:
                print(f"Error saving chat: {e}")
        else:
            error_message = f"Sorry, I couldn't process your question. {result.get('error', '')} {result.get('message', '')}"
            st.session_state.chat_history.append({
                "role": "bot", 
                "content": error_message
            })