import streamlit as st
import database

st.write(database.__file__)
st.stop()
 

import streamlit as st
from pathlib import Path

# ----------------------------------------
# Application Modules
# ----------------------------------------
from database import initialize_database
import config

from modules import (
    dashboard,
    course,
    co,
    po,
    mapping,
    preview,
    reports
)

# ----------------------------------------
# Database Initialization
# ----------------------------------------
initialize_database()

# ----------------------------------------
# Page Configuration
# ----------------------------------------
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout=config.LAYOUT,
    initial_sidebar_state="expanded"
)

# ----------------------------------------
# Load CSS
# ----------------------------------------
css_file = Path("assets/style.css")

if css_file.exists():
    with open(css_file) as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

# ----------------------------------------
# Sidebar
# ----------------------------------------
st.sidebar.title("🎓 OBE Analytics Pro")
st.sidebar.caption(f"Version {config.VERSION}")

page = st.sidebar.radio(
    "Navigation",
    config.MENU_ITEMS
)

st.sidebar.divider()

st.sidebar.info(
    "Outcome Based Education\n\n"
    "Single Course Version"
)

# ----------------------------------------
# Main Title
# ----------------------------------------
st.title("🎓 OBE Analytics Pro")

st.caption(
    "Outcome Based Education Analytics Platform"
)

st.divider()

# ----------------------------------------
# Navigation
# ----------------------------------------
try:

    if page == "🏠 Dashboard":
        dashboard.show()

    elif page == "📘 Course":
        course.show()

    elif page == "🎯 Course Outcomes":
        co.show()

    elif page == "🎓 Program Outcomes":
        po.show()

    elif page == "🔗 CO-PO Mapping":
        mapping.show()

    elif page == "👁 Preview":
        preview.show()

    elif page == "📄 Reports":
        reports.show()

except Exception as e:

    st.error("Application Error")

    st.exception(e)

# ----------------------------------------
# Footer
# ----------------------------------------
st.divider()

st.caption(
    "© 2026 OBE Analytics Pro | Developed using Streamlit & SQLite"
)