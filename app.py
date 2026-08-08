"""
=========================================================
OBE Analytics
app.py
---------------------------------------------------------
Main Application

Author : ChatGPT
=========================================================
"""

import streamlit as st
from database import initialize_database

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="OBE Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Initialize Database
# ---------------------------------------------------------

initialize_database()

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("🎓 OBE Analytics")
st.caption("Outcome Based Education Analytics System")

st.divider()

# ---------------------------------------------------------
# Welcome
# ---------------------------------------------------------

st.markdown(
    """
Welcome to **OBE Analytics**.

Use the **sidebar** to navigate through the modules.

### Modules

- 📘 Course
- 🎯 Course Outcomes (COs)
- 📝 Student Marks
- 🔗 CO–PO Mapping
- 📊 CO Attainment
- 📈 PO Attainment
- 📄 Reports

---
"""
)

# ---------------------------------------------------------
# Dashboard Metrics (Placeholder)
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Courses", "0")

with col2:
    st.metric("COs", "0")

with col3:
    st.metric("Students", "0")

with col4:
    st.metric("POs", "12")

st.divider()

st.info(
    "Create your first course from **Course** in the sidebar to begin."
)

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.markdown("---")
st.caption("OBE Analytics | Version 1.0")