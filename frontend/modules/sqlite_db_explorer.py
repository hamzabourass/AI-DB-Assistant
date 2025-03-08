# modules/sqlite_db_explorer.py
import streamlit as st
import sqlite3
import pandas as pd
import os
import sys
import json
from pathlib import Path

def render_sqlite_db_explorer_page():
    """Render a page to explore the SQLite database."""
    st.title("SQLite Database Explorer")
    
    # Path to the database - adjusted for backend folder
    # Get the current directory (frontend)
    current_dir = Path.cwd()
    # Navigate to the parent directory and then to backend/database
    backend_dir = current_dir.parent / "backend"
    db_path = backend_dir / "database" / "history.db"
    
    # Check if database exists
    if not db_path.exists():
        st.error(f"Database file not found at: {db_path}")
        st.info("Please verify the database path in the code if you're sure the database exists.")
        
        # Debugging info
        with st.expander("Debug Info"):
            st.write("Current directory:", current_dir)
            st.write("Expected backend directory:", backend_dir)
            st.write("Expected database path:", db_path)
            st.write("Parent directory contents:", [str(p) for p in current_dir.parent.iterdir()])
            if backend_dir.exists():
                st.write("Backend directory contents:", [str(p) for p in backend_dir.iterdir()])
                db_dir = backend_dir / "database"
                if db_dir.exists():
                    st.write("Database directory contents:", [str(p) for p in db_dir.iterdir()])
        
        # Custom path input
        custom_path = st.text_input(
            "Enter custom database path:",
            value=str(db_path)
        )
        
        if st.button("Try Custom Path"):
            db_path = Path(custom_path)
            if not db_path.exists():
                st.error(f"Database still not found at: {custom_path}")
                return
            st.success(f"Database found at: {custom_path}")
        else:
            return
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        
        # Get list of tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            st.warning("No tables found in the database.")
            return
            
        # Format table names for selection
        table_names = [table[0] for table in tables]
        
        # Database info
        st.success(f"Connected to database: {db_path}")
        st.write(f"Found {len(table_names)} tables")
        
        # Select table to view
        selected_table = st.selectbox("Select a table to view:", table_names)
        
        if selected_table:
            # Get table info
            cursor.execute(f"PRAGMA table_info({selected_table})")
            columns_info = cursor.fetchall()
            
            # Show table schema
            with st.expander("Table Schema", expanded=False):
                schema_df = pd.DataFrame(columns_info, 
                                         columns=['cid', 'name', 'type', 'notnull', 'default_value', 'pk'])
                st.dataframe(schema_df)
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {selected_table}")
            row_count = cursor.fetchone()[0]
            st.write(f"Total rows: {row_count}")
            
            # Query options
            st.subheader("Query Options")
            
            # Get column names
            column_names = [col[1] for col in columns_info]
            
            # Option to select specific columns
            selected_columns = st.multiselect(
                "Select columns to display (leave empty for all):",
                options=column_names,
                default=[]
            )
            
            # Filter options
            with st.expander("Filter Options", expanded=False):
                filter_column = st.selectbox(
                    "Filter by column:",
                    options=["None"] + column_names
                )
                
                filter_value = None
                if filter_column != "None":
                    filter_value = st.text_input("Filter value:")
            
            # Limit results option
            limit = st.number_input("Limit number of rows:", min_value=1, max_value=1000, value=100)
            
            # Execute query button
            if st.button("Execute Query"):
                # Construct SQL query
                columns_str = ", ".join(selected_columns) if selected_columns else "*"
                query = f"SELECT {columns_str} FROM {selected_table}"
                
                # Add WHERE clause if filter is applied
                if filter_column != "None" and filter_value:
                    query += f" WHERE {filter_column} LIKE '%{filter_value}%'"
                
                # Add LIMIT clause
                query += f" LIMIT {limit}"
                
                # Execute and display results
                results = pd.read_sql_query(query, conn)
                
                st.subheader("Query Results")
                st.code(query, language="sql")
                
                if results.empty:
                    st.info("No results found.")
                else:
                    st.dataframe(results, use_container_width=True)
                    
                    # Download option
                    csv = results.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Download as CSV",
                        csv,
                        f"{selected_table}_export.csv",
                        "text/csv",
                        key='download-csv'
                    )
            
            # Option for custom SQL query
            st.subheader("Custom SQL Query")
            custom_query = st.text_area(
                "Enter a custom SQL query:",
                value=f"SELECT * FROM {selected_table} LIMIT 10;"
            )
            
            if st.button("Run Custom Query"):
                try:
                    custom_results = pd.read_sql_query(custom_query, conn)
                    
                    if custom_results.empty:
                        st.info("No results found.")
                    else:
                        st.dataframe(custom_results, use_container_width=True)
                        
                        # Download option for custom query
                        custom_csv = custom_results.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "Download Custom Query Results",
                            custom_csv,
                            "custom_query_export.csv",
                            "text/csv",
                            key='download-custom-csv'
                        )
                except Exception as e:
                    st.error(f"Error executing query: {str(e)}")
        
        # Close connection
        conn.close()
        
    except sqlite3.Error as e:
        st.error(f"Database error: {str(e)}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")