import streamlit as st
import pandas as pd

from database.co_distribution import (
    get_courses,
    get_distribution
)

from engine.distribution import save_course_distribution


st.set_page_config(
    page_title="CO Distribution",
    page_icon="📊",
    layout="wide"
)

st.title("📊 CO Distribution")

# ---------------------------------------------------------
# Load Courses
# ---------------------------------------------------------

courses = get_courses()

if not courses:
    st.warning("No courses found. Please create a course first.")
    st.stop()

course_dict = {
    f"{code} - {name}": code
    for code, name in courses
}

selected = st.selectbox(
    "Select Course",
    list(course_dict.keys())
)

course_code = course_dict[selected]

# ---------------------------------------------------------
# Default Matrix
# ---------------------------------------------------------

matrix = {
    "LE": {"CO1": 5, "CO2": 5, "CO3": 5, "CO4": 5, "CO5": 5},
    "S1": {"CO1": 15, "CO2": 15, "CO3": 0, "CO4": 0, "CO5": 0},
    "S2": {"CO1": 0, "CO2": 0, "CO3": 15, "CO4": 15, "CO5": 15}
}

existing = get_distribution(course_code)

if existing:

    matrix = {"LE": {}, "S1": {}, "S2": {}}

    for assessment, co, marks in existing:
        matrix[assessment][co] = marks

# ---------------------------------------------------------
# Editable Table
# ---------------------------------------------------------

rows = []

for assessment in ["LE", "S1", "S2"]:

    row = {"Assessment": assessment}

    total = 0

    for co in ["CO1", "CO2", "CO3", "CO4", "CO5"]:

        value = matrix.get(assessment, {}).get(co, 0)

        row[co] = value

        total += value

    row["Total"] = total

    rows.append(row)

df = pd.DataFrame(rows)

edited = st.data_editor(
    df,
    use_container_width=True,
    hide_index=True,
    disabled=["Assessment", "Total"]
)

# ---------------------------------------------------------
# Live Totals
# ---------------------------------------------------------

edited.loc[0, "Total"] = edited.loc[0, ["CO1", "CO2", "CO3", "CO4", "CO5"]].sum()
edited.loc[1, "Total"] = edited.loc[1, ["CO1", "CO2", "CO3", "CO4", "CO5"]].sum()
edited.loc[2, "Total"] = edited.loc[2, ["CO1", "CO2", "CO3", "CO4", "CO5"]].sum()

st.subheader("Validation")

c1, c2, c3 = st.columns(3)

with c1:
    if edited.loc[0, "Total"] == 25:
        st.success("LE = 25")
    else:
        st.error(f"LE = {edited.loc[0,'Total']}")

with c2:
    if edited.loc[1, "Total"] == 30:
        st.success("S1 = 30")
    else:
        st.error(f"S1 = {edited.loc[1,'Total']}")

with c3:
    if edited.loc[2, "Total"] == 45:
        st.success("S2 = 45")
    else:
        st.error(f"S2 = {edited.loc[2,'Total']}")

# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

if st.button("💾 Save Distribution", use_container_width=True):

    save_matrix = {}

    for _, row in edited.iterrows():

        assessment = row["Assessment"]

        save_matrix[assessment] = {}

        for co in ["CO1", "CO2", "CO3", "CO4", "CO5"]:

            save_matrix[assessment][co] = float(row[co])

    success, messages = save_course_distribution(
        course_code,
        save_matrix
    )

    if success:
        st.success(messages[0])
    else:
        for msg in messages:
            st.error(msg)