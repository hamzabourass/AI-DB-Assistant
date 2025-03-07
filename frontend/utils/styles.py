import streamlit as st

def load_css():
    """Load custom CSS for the application."""
    st.markdown("""
    <style>
        /* Ultra minimal styling */
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #333;
        }
        
                section[data-testid="stSidebar"] {
            background-color: #f8f9fa;
            border-right: 1px solid #eee;
        }

        section[data-testid="stSidebar"] h1 {
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
        }

        section[data-testid="stSidebar"] h3 {
            font-size: 1rem;
            color: #555;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }

        /* Navigation button styling */
        section[data-testid="stSidebar"] button {
            background-color: transparent;
            border: none;
            text-align: left;
            color: #333;
            padding: 0.5rem 0;
            transition: background-color 0.2s;
        }

        section[data-testid="stSidebar"] button:hover {
            background-color: #f0f2f6;
        }

        /* Active navigation item - you'll need to add classes in your code */
        .nav-active {
            background-color: #e6f0ff !important;
            color: #1f77b4 !important;
            font-weight: 500;
        }

        /* Remove default button styling */
        section[data-testid="stSidebar"] .stButton > button {
            border: none;
            box-shadow: none;
        }

        /* Make dividers lighter */
        section[data-testid="stSidebar"] hr {
            margin: 1rem 0;
            border-color: #eee;
        }
        /* Simple form elements */
        .stTextInput > div > div > input, 
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > div {
            border: 1px solid #ddd;
            border-radius: 3px;
        }
        
        /* Simple button */
        .stButton > button {
            border-radius: 3px;
        }
        
        /* Clean tabs - just an underline, no boxes */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            border-bottom: 1px solid #ddd;
        }
        
        .stTabs [data-baseweb="tab"] {
            border: none !important;
            background-color: transparent !important;
            border-radius: 0;
            border-bottom: 2px solid transparent !important;
            color: #555;
        }
        
        .stTabs [aria-selected="true"] {
            color: #4285F4 !important;
            border-bottom-color: #4285F4 !important;
        }
        
        /* Remove decorative elements */
        .decoration {
            display: none;
        }
        
        /* Clean expander */
        .streamlit-expanderHeader {
            color: #555;
        }
        
        /* Hide footer */
        footer {
            visibility: hidden;
        }
        
        /* History list styling */
        hr {
            margin: 1.5rem 0;
            border: none;
            border-top: 1px solid #eee;
        }
    </style>
    """, unsafe_allow_html=True)