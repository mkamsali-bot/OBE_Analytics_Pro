"""
OBE Analytics Pro v1.0.0
Main Application
"""

import streamlit as st

from config import (
    APP_NAME,
    VERSION,
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
    MENU_ITEMS,
)

from database import initialize_database

# ---------------------------------
# Initialize Database
# ---------------------------------
initialize_database()

# ---------------------------------
# Page Configuration
# ---------------------------------
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
)

# ---------------------------------
# Load CSS
# ---------------------------------
try:
    with open("assets/style.css") as css:
        st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# ---------------------------------
# Sidebar
# ---------------------------------
st.sidebar.title("🎓 OBE Analytics Pro")
st.sidebar.caption(f"Version {VERSION}")

page = st.sidebar.radio(
    "Navigation",
    MENU_ITEMS,
)

# ---------------------------------
# Dashboard
# ---------------------------------
if page == "🏠 Dashboard":
    from modules.dashboard import show_dashboard
    show_dashboard()

# ---------------------------------
# Placeholder Modules
# ---------------------------------
else:
    st.title(page)
    st.info("🚧 This module will be implemented in the next milestone.")