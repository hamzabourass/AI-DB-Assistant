import streamlit as st
from utils.api import check_api_status

def render_home_page():
    """Render the home page of the application."""
    st.markdown("<h1 class='main-header'>AI Database Assistant</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <h3>Welcome to the AI Database Assistant! 👋</h3>
        <p>This intelligent tool leverages the power of AI to help you work with databases more efficiently. 
        Whether you need to generate SQL queries, learn about database concepts, or design database schemas, 
        we've got you covered.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features section
    st.markdown("<h2 class='sub-header'>Features</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card sql-feature feature-card">
            <div class="feature-icon">📝</div>
            <h3>SQL Generator</h3>
            <p>Convert natural language to SQL queries for any database dialect. Simply describe what data you need, and our AI will generate the appropriate SQL.</p>
            <span class="status-badge success">Available</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card knowledge-feature feature-card">
            <div class="feature-icon">🔍</div>
            <h3>DB Knowledge</h3>
            <p>Get answers to database questions and learn best practices. Ask about concepts, syntax, optimization techniques, and more.</p>
            <span class="status-badge pending">Coming Soon</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card schema-feature feature-card">
            <div class="feature-icon">🏗️</div>
            <h3>Schema Designer</h3>
            <p>Generate database schemas from natural language descriptions. Describe your requirements and get a complete schema design.</p>
            <span class="status-badge pending">Coming Soon</span>
        </div>
        """, unsafe_allow_html=True)
    
    # System status
    st.markdown("<h2 class='sub-header'>System Status</h2>", unsafe_allow_html=True)
    
    api_status = check_api_status()
    status_card = st.container()
    
    with status_card:
        if api_status["connected"]:
            st.success("✅ Backend API is connected and running properly")
            st.markdown("""
            <div class="card">
                <h4>All Systems Operational</h4>
                <p>The application is fully functional. Feel free to explore all available features.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ Cannot connect to backend API")
            st.markdown("""
            <div class="card">
                <h4>Connection Issue Detected</h4>
                <p>The application is running but cannot connect to the backend API. This means some features will not work properly.</p>
                <ul>
                    <li>Please ensure the API server is running at http://localhost:8000</li>
                    <li>Check network connections and firewall settings</li>
                    <li>Contact your administrator if the problem persists</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # Quick start section
    st.markdown("<h2 class='sub-header'>Quick Start</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <h4>How to use the AI Database Assistant:</h4>
        <ol>
            <li>Select a feature from the sidebar navigation</li>
            <li>Follow the instructions for each tool</li>
            <li>For the SQL Generator, describe what data you want to query in natural language</li>
            <li>Review and use the generated output in your database system</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)