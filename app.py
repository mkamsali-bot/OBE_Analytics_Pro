"""
OBE Analytics Pro
Version 1.1.2
Main Application
"""

import streamlit as st

from database import initialize_database

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="OBE Analytics Pro",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# DATABASE INITIALIZATION
# ---------------------------------------------------------

initialize_database()

# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------

st.title("🎓 OBE Analytics Pro")

st.markdown(
    """
### Outcome Based Education Analytics System

Welcome to **OBE Analytics Pro**.

Use the navigation panel on the left to access the modules.
"""
)

st.info(
    "Select a page from the sidebar to begin."
)