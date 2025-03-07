# modules/sql_generator.py
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.api import generate_sql, get_sql_history, get_sql_history_by_id, delete_sql_history
import os
import sqlite3

def format_timestamp(timestamp_str):
    """Format timestamp string to a more readable format."""
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return timestamp_str


def render_sql_generator_page():
    """Render the SQL Generator page."""
    # Initialize session state
    if "description" not in st.session_state:
        st.session_state.description = ""
    if "dialect" not in st.session_state:
        st.session_state.dialect = "MySQL"
    
    # Page header
    st.title("SQL Query Generator")
    
    # Simple tabs
    tab1, tab2 = st.tabs(["Generator", "History"])
    
    # Generator Tab
    with tab1:
        st.header("Generate SQL from natural language")
        
        # SQL dialect selector
        dialect = st.selectbox(
            "Database Type",
            ["MySQL", "PostgreSQL", "SQLite", "SQL Server", "Oracle"],
            index=["MySQL", "PostgreSQL", "SQLite", "SQL Server", "Oracle"].index(st.session_state.dialect)
        )
        
        # Query description input
        description = st.text_area(
            "Describe what data you want to query:",
            value=st.session_state.description,
            placeholder="Example: Find all customers who made a purchase over $100 in the last month",
            height=120
        )
        
        # Generate button
        if st.button("Generate SQL", type="primary"):
            if not description:
                st.error("Please enter a description of what you want to query.")
            else:
                # Save values to session state
                st.session_state.description = description
                st.session_state.dialect = dialect
                
                with st.spinner("Generating SQL query..."):
                    result = generate_sql(description, dialect)
                    
                    if result["success"]:
                        st.success("SQL Generated Successfully")
                        
                        # Display the generated SQL
                        st.subheader("Generated SQL")
                        st.code(result["sql"], language="sql", line_numbers=True)
                      
                    else:
                        st.error(f"Error: {result.get('error', '')}")
                        st.error(f"Message: {result.get('message', 'Failed to generate SQL')}")
        
        # Simple tips section
        with st.expander("Tips for better results"):
            st.markdown("""
            - Be specific about the data you want
            - Mention table names if you know them
            - Specify any conditions or filters clearly
            - Include time periods if relevant
            """)
    
    # History Tab
    with tab2:
        st.header("Query History")
        
        # Refresh button
        if st.button("Refresh History"):
            st.rerun()
        
        # Get history data
        with st.spinner("Loading history..."):
            history_result = get_sql_history()
        
        if history_result["success"] and history_result["history"]:
            # Display history items one by one in a simple list
            for item in history_result["history"]:
                with st.container():
                    # Top row with metadata and actions
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**ID: {item['id']} • {format_timestamp(item['timestamp'])} • {item['dialect']}**")
                    
                    with col3:
                        # Delete button for this item
                        if st.button("Delete", key=f"delete_{item['id']}"):
                            with st.spinner("Deleting..."):
                                delete_result = delete_sql_history(item['id'])
                            
                            if delete_result["success"]:
                                st.success(f"Query #{item['id']} deleted!")
                                st.rerun()
                            else:
                                st.error("Delete failed.")
                    
                    # Description row
                    st.markdown(f"**Description:** {item['description']}")
                    
                    # SQL query row
                    st.markdown("**SQL:**")
                    st.code(item["generated_sql"], language="sql")

                    
                    # Divider between items
                    st.markdown("---")
        
        elif history_result["success"] and not history_result["history"]:
            st.info("No history found. Generate some SQL queries to see them here!")
        else:
            st.error("Could not load history. Please check your connection to the API.")