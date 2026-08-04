import streamlit as st


def show_dashboard():

    st.title("🎓 OBE Analytics Pro")

    st.subheader("Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Course", "Not Configured")
    col2.metric("COs", "0")
    col3.metric("POs", "12")
    col4.metric("Mappings", "0")

    st.divider()

    st.success("✅ Milestone 1 completed successfully.")

    st.markdown(
        """
### Version 1.0 Modules

- Dashboard
- Course
- Course Outcomes
- Program Outcomes
- CO–PO Mapping
- Preview
- Reports
"""
    )