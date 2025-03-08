import streamlit as st
from modules.home import render_home_page
from modules.sql_generator import render_sql_generator_page
from modules.db_knowledge import render_db_knowledge_page
from modules.vector_db_explorer import render_vector_db_explorer_page
from utils.api import check_api_status
from utils.styles import load_css

# Page configuration
st.set_page_config(
    page_title="AI Database Assistant",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_css()

# Sidebar configuration
def render_sidebar():
    with st.sidebar:
        st.title("AI Database Assistant")
        
        # Navigation
        st.subheader("Navigation")
        page = st.selectbox(
            "Select a feature:",
            ["Home", "Database Assistant Chat", "Vector Database Explorer"]
        )
        
        st.divider()
        
        # About section
        st.markdown("### About")
        st.markdown("""
        This tool uses AI to simplify database-related tasks:
        - Generate SQL queries
        - Manage database connections
        - Browse database schemas
        - Answer database questions
        - Design database schemas
        """)
        
        st.divider()
        
        # Backend status indicator
        api_status = check_api_status()
        if api_status["connected"]:
            st.success("✅ API Connected", icon="✅")
        else:
            st.error("❌ API Disconnected", icon="❌")
        
        st.caption("Version 0.4")
    
    return page

# Main application
def main():
    # Render sidebar and get selected page
    selected_page = render_sidebar()

    if selected_page == "Home":
        render_home_page()
    elif selected_page == "Database Assistant Chat":
        render_db_knowledge_page()
    elif selected_page == "SQL Generator":
        render_sql_generator_page()
    elif selected_page == "Vector Database Explorer":
        render_vector_db_explorer_page()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>AI Database Assistant v0.4 | Developed with Streamlit & AI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()