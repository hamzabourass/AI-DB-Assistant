# modules/sql_generator.py
import streamlit as st
from utils.api import generate_sql

def render_sql_generator_page():
    """Render the SQL Generator page."""
    # Page header
    st.markdown("<h1 class='main-header'>SQL Query Generator</h1>", unsafe_allow_html=True)
    
    # Information card
    st.markdown("""
    <div class="card sql-feature">
        <h3>AI-Powered SQL Generation</h3>
        <p>Transform your natural language descriptions into precise SQL queries. 
        Our AI understands your intent and generates the appropriate SQL code for your database.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content area - now using full width without examples section
    with st.form("sql_form"):
        # Query description input
        description = st.text_area(
            "Describe what data you want to query:",
            placeholder="Example: Find all customers who made a purchase over $100 in the last month and are subscribed to the newsletter",
            height=150
        )
        
        # SQL dialect selector in a cleaner layout
        col_a, col_b, col_c = st.columns([1, 1, 2])
        with col_a:
            dialect = st.selectbox(
                "SQL Dialect", 
                ["MySQL", "PostgreSQL", "SQLite", "SQL Server", "Oracle"]
            )
        
        # Submit button with centered layout
        col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 1])
        with col_submit2:
            submitted = st.form_submit_button("🔍 Generate SQL")
    
    # Handle form submission
    if submitted and description:
        with st.spinner("Generating SQL query..."):
            result = generate_sql(description, dialect)
            
            if result["success"]:
                st.success(f"SQL query generated successfully for {dialect}!")
                
                # Display the generated SQL
                st.markdown("<h3 class='sub-header'>Generated SQL</h3>", unsafe_allow_html=True)
                st.code(result["sql"], language="sql", line_numbers=True)
                
                # Copy message
                st.markdown("""
                <div class="card sql-feature" style="padding: 0.75rem;">
                    <p style="margin-bottom: 0.5rem;">Copy this query to your database tool to execute it.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Edit options
                with st.expander("Need to make adjustments?"):
                    edited_sql = st.text_area("Edit SQL:", value=result["sql"], height=200)
                    if edited_sql != result["sql"]:
                        st.markdown("<div class='card'>", unsafe_allow_html=True)
                        st.markdown("#### Your Edited SQL")
                        st.code(edited_sql, language="sql", line_numbers=True)
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error(result["error"])
                st.error(result["message"])
                
                st.markdown("""
                <div class="card" style="border-top-color: #ef4444;">
                    <h4>Troubleshooting</h4>
                    <ul>
                        <li>Check that the API server is running</li>
                        <li>Try simplifying your query description</li>
                        <li>Check network connectivity</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
    
    # Tips section at the bottom - simplified to one column
    st.markdown("<h3 class='sub-header'>Tips for Better Results</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <h4>Writing Effective Descriptions</h4>
        <ul>
            <li>Be specific about the data you want</li>
            <li>Mention table names if you know them</li>
            <li>Specify any conditions or filters clearly</li>
            <li>Include time periods if relevant</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)