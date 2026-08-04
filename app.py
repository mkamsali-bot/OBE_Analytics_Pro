
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
# Load CSS
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

# ==========================================
# Dashboard
# ==========================================
if page == "🏠 Dashboard":
    from modules.dashboard import show_dashboard
    show_dashboard()

# ==========================================
# Course
# ==========================================
elif page == "📘 Course":
    from modules.course import show_course
    show_course()

# ==========================================
# Course Outcomes
# ==========================================
elif page == "🎯 Course Outcomes":
    from modules.co import show_co
    show_co()

# ==========================================
# Program Outcomes
# ==========================================
elif page == "🎓 Program Outcomes":
    from modules.po import show_po
    show_po()

# ==========================================
# CO-PO Mapping
# ==========================================
elif page == "🔗 CO-PO Mapping":
    from modules.mapping import show_mapping
    show_mapping()

# ==========================================
# Preview
# ==========================================
elif page == "👁 Preview":
    from modules.preview import show_preview
    show_preview()

# ==========================================
# Reports
# ==========================================
elif page == "📄 Reports":
    from modules.reports import show_reports
    show_reports()