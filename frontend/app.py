import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="AI Database Assistant",
    page_icon="🗄️"
)

st.title("AI Database Assistant")
st.write("This application will help with database questions, SQL generation, and schema design.")

st.subheader("Backend Connection Test")

if st.button("Test Connection"):
    try:
        response = requests.get(f"{API_URL}/api/test")
        if response.status_code == 200:
            st.success(f"Connected to backend: {response.json()['message']}")
        else:
            st.error(f"Error: Received status code {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("Failed to connect to backend. Make sure the API server is running.")