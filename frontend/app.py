import streamlit as st
from modules.home import render_home_page
from modules.sql_generator import render_sql_generator_page
from modules.db_knowledge import render_db_knowledge_page
from modules.schema_designer import render_schema_designer_page
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
        page = st.radio(
            "Select a feature:",
            ["Home", "SQL Generator", "DB Knowledge", "Schema Designer"]
        )
        
        st.divider()
        
        # About section
        st.markdown("### About")
        st.markdown("""
        This tool uses AI to simplify database-related tasks:
        - Generate SQL queries
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
        
        st.caption("Version 0.2")
    
    return page

# Main application
def main():
    # Render sidebar and get selected page
    selected_page = render_sidebar()
    
    # Display the selected page
    if selected_page == "Home":
        render_home_page()
    elif selected_page == "SQL Generator":
        render_sql_generator_page()
    elif selected_page == "DB Knowledge":
        render_db_knowledge_page()
    elif selected_page == "Schema Designer":
        render_schema_designer_page()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>AI Database Assistant v0.2 | Developed with Streamlit & AI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()