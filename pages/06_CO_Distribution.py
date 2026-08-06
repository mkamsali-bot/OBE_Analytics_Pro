"""
pages/06_CO_Distribution.py
OBE Analytics Pro v1.2 RC1
"""

import streamlit as st
import pandas as pd

from database.co_distribution import (
    get_courses,
    get_distribution,
    save_distribution,
    delete_distribution,
)

st.title("📊 CO Distribution")
st.caption("Manage Course Outcome (CO) Distribution")

courses = get_courses()

if not courses:
    st.warning("No courses found.")
    st.stop()

course_map = {f"{r[0]} - {r[1]}": r[0] for r in courses}
selected = st.selectbox("Course", list(course_map.keys()))
course_code = course_map[selected]

saved = get_distribution(course_code)

if saved:
    df = pd.DataFrame(saved, columns=[
        "Assessment",
        "CO",
        "Allocated Marks"
    ])
else:
    df = pd.DataFrame(columns=[
        "Assessment",
        "CO",
        "Allocated Marks"
    ])

edited = st.data_editor(
    df,
    column_config={
        "Assessment": st.column_config.SelectboxColumn(
            "Assessment",
            options=["LE","S1","S2","Assignment","Quiz"]
        ),
        "CO": st.column_config.TextColumn("CO"),
        "Allocated Marks": st.column_config.NumberColumn(
            "Allocated Marks",
            min_value=0,
            step=1
        ),
    },
    num_rows="dynamic",
    hide_index=True,
    use_container_width=True,
)

st.divider()

c1, c2 = st.columns(2)

with c1:
    if st.button("💾 Save Distribution", use_container_width=True):
        data = []
        for _, row in edited.iterrows():
            if pd.notna(row["Assessment"]) and pd.notna(row["CO"]):
                marks = int(row["Allocated Marks"]) if pd.notna(row["Allocated Marks"]) else 0
                data.append((row["Assessment"], row["CO"], marks))
        save_distribution(course_code, data)
        st.success("Distribution saved successfully.")
        st.rerun()

with c2:
    if st.button("🗑 Clear Distribution", use_container_width=True):
        delete_distribution(course_code)
        st.success("Distribution deleted.")
        st.rerun()

st.divider()

st.subheader("Summary")

if not edited.empty:
    summary = edited.groupby("Assessment", dropna=False)["Allocated Marks"].sum().reset_index()
    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.metric("Total Entries", len(edited))
    st.metric("Total Marks", int(edited["Allocated Marks"].fillna(0).sum()))
else:
    st.info("No distribution available for the selected course.")
