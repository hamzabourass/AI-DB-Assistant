import streamlit as st

def load_css():
    """Load custom CSS for the application."""
    st.markdown("""
    <style>
        /* Color palette */
        :root {
            --primary: #3b82f6;
            --primary-dark: #1d4ed8;
            --secondary: #8b5cf6;
            --tertiary: #ec4899;
            --success: #10b981;
            --warning: #f59e0b;
            --light-bg: #f8fafc;
            --dark-text: #1e293b;
            --light-text: #f8fafc;
            --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        
        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Helvetica Neue', sans-serif;
        }
        
        /* Main containers and headers */
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary-dark);
            margin-bottom: 1.5rem;
            text-align: center;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--primary);
        }
        
        .sub-header {
            font-size: 1.8rem;
            font-weight: 600;
            color: var(--primary);
            margin: 1.5rem 0 1rem 0;
            padding-bottom: 0.25rem;
            border-bottom: 1px solid #e2e8f0;
        }
        
        /* Cards and containers */
        .card {
            background-color: var(--light-bg);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: var(--card-shadow);
            margin-bottom: 1.5rem;
            border-top: 4px solid var(--primary);
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        
        /* Feature cards */
        .feature-card {
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        .sql-feature {border-top-color: var(--primary);}
        .knowledge-feature {border-top-color: var(--secondary);}
        .schema-feature {border-top-color: var(--tertiary);}
        
        /* Status indicators */
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 600;
            margin-top: 0.5rem;
        }
        
        .status-badge.success {
            background-color: rgba(16, 185, 129, 0.1);
            color: var(--success);
            border: 1px solid var(--success);
        }
        
        .status-badge.pending {
            background-color: rgba(245, 158, 11, 0.1);
            color: var(--warning);
            border: 1px solid var(--warning);
        }
        
        /* Form elements */
        .stTextInput > div > div > input, .stTextArea > div > div > textarea {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 0.75rem;
            transition: border-color 0.2s ease-in-out;
        }
        
        .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
        }
        
        /* Button styling */
        .stButton > button {
            background-color: var(--primary);
            color: var(--light-text);
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: 600;
            border: none;
            transition: background-color 0.2s ease-in-out;
        }
        
        .stButton > button:hover {
            background-color: var(--primary-dark);
        }
        
        /* Select box styling */
        .stSelectbox > div > div > div {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
        }
        
        /* Footer */
        .footer {
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid #e2e8f0;
            text-align: center;
            color: #64748b;
            font-size: 0.875rem;
        }
        
        /* Code display */
        .sql-code {
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            font-family: 'Courier New', monospace;
        }
        
        /* Sidebar styling */
        .css-18e3th9 {
            padding-top: 2rem;
        }
        
        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .main-header {
                font-size: 2rem;
            }
            
            .sub-header {
                font-size: 1.5rem;
            }
            
            .card {
                padding: 1rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)