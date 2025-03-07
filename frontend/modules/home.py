import streamlit as st
from utils.api import check_api_status

def render_home_page():
    """Render the home page of the application."""
    # Main title
    st.title("AI Database Assistant")
    
    # Introduction card
    st.markdown("""
    <div style="
        padding: 20px; 
        border-radius: 8px; 
        background-color: white; 
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    ">
        <h3>Welcome to the AI Database Assistant 👋</h3>
        <p>This tool helps you work with databases more efficiently by leveraging artificial intelligence.
        Whether you need to write SQL queries, learn about database concepts, or design database schemas,
        we've got you covered.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features section
    st.markdown("""
    <h2 style="margin-top: 30px; margin-bottom: 20px;">Features</h2>
    """, unsafe_allow_html=True)
    
    # Features in a card layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            padding: 20px; 
            border-radius: 8px; 
            background-color: white; 
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            height: 100%;
        ">
            <div style="font-size: 2rem; margin-bottom: 10px;">📝</div>
            <h3>SQL Generator</h3>
            <p>Convert natural language to SQL queries for any database dialect.</p>
            <div style="
                display: inline-block;
                padding: 4px 8px;
                background-color: #e6f4ea;
                color: #137333;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: 500;
            ">
                Available
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            padding: 20px; 
            border-radius: 8px; 
            background-color: white; 
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            height: 100%;
        ">
            <div style="font-size: 2rem; margin-bottom: 10px;">🔍</div>
            <h3>DB Knowledge</h3>
            <p>Get answers to database questions and learn best practices.</p>
            <div style="
                display: inline-block;
                padding: 4px 8px;
                background-color: #fef7e0;
                color: #b06000;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: 500;
            ">
                Coming Soon
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="
            padding: 20px; 
            border-radius: 8px; 
            background-color: white; 
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            height: 100%;
        ">
            <div style="font-size: 2rem; margin-bottom: 10px;">🏗️</div>
            <h3>Schema Designer</h3>
            <p>Generate database schemas from natural language descriptions.</p>
            <div style="
                display: inline-block;
                padding: 4px 8px;
                background-color: #fef7e0;
                color: #b06000;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: 500;
            ">
                Coming Soon
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # System status card
    st.markdown("""
    <h2 style="margin-top: 30px; margin-bottom: 20px;">System Status</h2>
    """, unsafe_allow_html=True)
    
    api_status = check_api_status()
    
    if api_status["connected"]:
        status_color = "#e6f4ea"
        status_text_color = "#137333"
        status_message = "✅ Backend API is connected and running properly"
    else:
        status_color = "#fce8e6"
        status_text_color = "#c5221f"
        status_message = "❌ Cannot connect to backend API"
    
    st.markdown(f"""
    <div style="
        padding: 20px; 
        border-radius: 8px; 
        background-color: {status_color}; 
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        color: {status_text_color};
    ">
        <h3 style="color: {status_text_color};">System Status</h3>
        <p style="font-weight: 500;">{status_message}</p>
        
        {"" if api_status["connected"] else """
        <p><strong>Please check:</strong></p>
        <ul>
            <li>API server is running at http://localhost:8000</li>
            <li>Network connections and firewall settings</li>
        </ul>
        """}
    </div>
    """, unsafe_allow_html=True)
    
    # Quick start card
    st.markdown("""
    <h2 style="margin-top: 30px; margin-bottom: 20px;">Quick Start</h2>
    <div style="
        padding: 20px; 
        border-radius: 8px; 
        background-color: white; 
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    ">
        <h3>How to use the AI Database Assistant</h3>
        <ol>
            <li>Select a feature from the sidebar navigation</li>
            <li>Follow the instructions for each tool</li>
            <li>For the SQL Generator, describe what data you want to query in natural language</li>
            <li>Review and use the generated output in your database system</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("How it works"):
        with st.container():
            st.markdown("""
                The AI Database Assistant uses natural language processing to understand your requests and generate 
                appropriate database-related outputs:

                - **SQL Generator**: Translates your description into valid SQL code
                - **DB Knowledge**: Provides explanations about database concepts and best practices
                - **Schema Designer**: Creates database schemas based on your requirements

                All of this is powered by advanced language models that understand both natural language and database technologies.
            """)
            st.markdown("""
                <style>
                    div[data-testid="stContainer"] {
                        padding: 20px; 
                        border-radius: 8px; 
                        background-color: #f8f9fa;
                    }
                </style>
            """, unsafe_allow_html=True)