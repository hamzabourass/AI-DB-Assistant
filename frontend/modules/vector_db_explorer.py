import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import io
from utils.api import (
    get_vector_db_stats, 
    get_vector_db_documents, 
    get_vector_db_document,
    search_vector_db,
    upload_knowledge_document
)

def render_vector_db_explorer_page():
    """Render the Vector Database Explorer page."""
    st.title("Vector Database Explorer")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Overview", "Document Explorer", "Search"])
    
    # Overview Tab
    with tab1:
        st.header("Vector Database Overview")
        
        # Refresh button
        if st.button("Refresh Statistics"):
            st.cache_data.clear()
        
        stats = get_vector_db_stats_cached()
        
        if "error" in stats:
            st.error(f"Error fetching statistics: {stats['error']}")
        else:
            # Display basic statistics
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Documents", stats.get("document_count", 0))
                st.metric("Embedding Dimensions", stats.get("embedding_dimensions", 0))
            
            with col2:
                st.metric("Avg. Document Length", f"{int(stats.get('average_document_length', 0))} chars")
                st.metric("Number of Sources", len(stats.get("sources", {})))
            
            # Show sources distribution
            if stats.get("sources"):
                st.subheader("Document Sources")
                
                # Convert to dataframe for display
                sources_df = pd.DataFrame({
                    "Source": list(stats["sources"].keys()),
                    "Count": list(stats["sources"].values())
                })
                
                sources_df = sources_df.sort_values("Count", ascending=False)
                
                # Create pie chart
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.pie(sources_df["Count"], labels=sources_df["Source"], autopct='%1.1f%%')
                ax.axis('equal')
                st.pyplot(fig)
                
                # Show as table
                st.dataframe(sources_df)
        
        # Upload new documents
        st.subheader("Upload New Document")
        
        uploaded_file = st.file_uploader("Choose a text file", type=["txt"])
        
        if uploaded_file is not None:
            if st.button("Upload and Index Document"):
                with st.spinner("Uploading and indexing document..."):
                    result = upload_knowledge_document(uploaded_file)
                
                if "error" in result:
                    st.error(f"Error uploading document: {result['error']}")
                else:
                    st.success(result.get("message", "Document uploaded successfully"))
                    # Clear the cache so new document appears
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()
    
    # Document Explorer Tab
    with tab2:
        st.header("Document Explorer")
        
        # Get documents with pagination
        page_size = 10
        current_page = st.session_state.get("current_page", 1)
        
        # Calculate offset
        offset = (current_page - 1) * page_size
        
        # Fetch documents
        docs_result = get_vector_db_documents_cached(limit=page_size, offset=offset)
        
        if "error" in docs_result:
            st.error(f"Error fetching documents: {docs_result['error']}")
        else:
            documents = docs_result.get("documents", [])
            total_docs = docs_result.get("total", 0)
            total_pages = (total_docs + page_size - 1) // page_size if total_docs > 0 else 1
            
            # Pagination controls
            col1, col2, col3, col4 = st.columns([1, 3, 3, 1])
            
            with col1:
                if current_page > 1:
                    if st.button("←"):
                        st.session_state.current_page = current_page - 1
                        st.rerun()
            
            with col2:
                st.write(f"Page {current_page} of {total_pages}")
            
            with col3:
                # Page number input
                page_input = st.number_input(
                    "Go to page", 
                    min_value=1, 
                    max_value=max(1, total_pages),
                    value=current_page,
                    label_visibility="collapsed"
                )
                
                if page_input != current_page:
                    st.session_state.current_page = page_input
                    st.rerun()
            
            with col4:
                if current_page < total_pages:
                    if st.button("→"):
                        st.session_state.current_page = current_page + 1
                        st.rerun()
            
            # Display documents
            if documents:
                for doc in documents:
                    with st.expander(f"Document: {doc.get('id', 'Unknown')}"):
                        st.markdown("#### Metadata")
                        metadata = doc.get("metadata", {})
                        
                        for key, value in metadata.items():
                            st.write(f"**{key}:** {value}")
                        
                        st.markdown("#### Content")
                        st.text_area(
                            "Document content",
                            value=doc.get("content", "No content available"),
                            height=200,
                            label_visibility="collapsed"
                        )
            else:
                st.info("No documents found in the vector database.")
    
    # Search Tab
    with tab3:
        st.header("Search Vector Database")
        
        query = st.text_input("Enter search query:")
        k = st.slider("Number of results:", min_value=1, max_value=20, value=5)
        
        if st.button("Search") and query:
            with st.spinner("Searching..."):
                results = search_vector_db(query, k)
            
            if "error" in results:
                st.error(f"Error searching: {results['error']}")
            else:
                search_results = results.get("results", [])
                
                if not search_results:
                    st.info("No matching documents found.")
                else:
                    for i, result in enumerate(search_results):
                        similarity = result.get("similarity_score", 0)
                        similarity_percentage = (1 - similarity) * 100  # Convert distance to similarity percentage
                        
                        with st.expander(f"Result {i+1} - Similarity: {similarity_percentage:.2f}%"):
                            st.markdown("#### Metadata")
                            metadata = result.get("metadata", {})
                            
                            for key, value in metadata.items():
                                st.write(f"**{key}:** {value}")
                            
                            st.markdown("#### Content")
                            st.text_area(
                                f"Document content {i}",
                                value=result.get("content", "No content available"),
                                height=200,
                                label_visibility="collapsed"
                            )

@st.cache_data(ttl=300)
def get_vector_db_stats_cached():
    """Cached version of get_vector_db_stats."""
    return get_vector_db_stats()

@st.cache_data(ttl=300)
def get_vector_db_documents_cached(limit=10, offset=0):
    """Cached version of get_vector_db_documents."""
    return get_vector_db_documents(limit, offset)