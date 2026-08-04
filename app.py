import streamlit as st

from database import (
    initialize_database,
    save_course,
    get_course,
    get_all_cos,
    add_co,
    delete_co
)


initialize_database()

st.set_page_config(
    page_title="OBE Analytics Pro",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 OBE Analytics Pro")
st.caption("Single Course CO–PO Mapping")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📘 Course", "🎯 COs", "🔗 Mapping", "👁 Preview", "📄 Reports"]
)

with tab1:

    st.subheader("Course Details")

    course = get_course()

    with st.form("course_form"):

        course_code = st.text_input(
            "Course Code",
            value=course["course_code"] if course else ""
        )

        course_name = st.text_input(
            "Course Name",
            value=course["course_name"] if course else ""
        )

        faculty = st.text_input(
            "Faculty Name",
            value=course["faculty"] if course else ""
        )

        department = st.text_input(
            "Department",
            value=course["department"] if course else ""
        )

        programme = st.text_input(
            "Programme",
            value=course["programme"] if course else ""
        )

        semester = st.number_input(
            "Semester",
            min_value=1,
            max_value=8,
            value=course["semester"] if course else 1
        )

        credits = st.number_input(
            "Credits",
            min_value=1,
            max_value=10,
            value=course["credits"] if course else 3
        )

        academic_year = st.text_input(
            "Academic Year",
            value=course["academic_year"] if course else "2026-27"
        )

        submitted = st.form_submit_button(
            "💾 Save Course",
            use_container_width=True
        )

        if submitted:

            save_course((
                course_code,
                course_name,
                faculty,
                department,
                programme,
                semester,
                credits,
                academic_year
            ))

            st.success("Course saved successfully.")
            st.rerun()
with tab2:

    st.subheader("🎯 Course Outcomes")

    # ---------- Add CO ----------
    with st.expander("➕ Add New CO", expanded=False):

        co_statement = st.text_area(
            "Course Outcome",
            height=100
        )

        bloom = st.selectbox(
            "Bloom's Level",
            ["L1", "L2", "L3", "L4", "L5", "L6"]
        )

        if st.button("Add CO"):

            if co_statement.strip() == "":
                st.warning("Enter Course Outcome")
            else:
                add_co(co_statement, bloom)
                st.success("CO Added")
                st.rerun()

    st.divider()

    cos = get_all_cos()

    if cos:

        st.write("### Existing Course Outcomes")

        for row in cos:

            c1, c2, c3, c4 = st.columns([1,6,1,1])

            with c1:
                st.write(row["co_no"])

            with c2:
                st.write(row["co_statement"])

            with c3:
                st.write(row["bloom_level"])

            with c4:
                if st.button("🗑", key=row["id"]):
                    delete_co(row["id"])
                    st.rerun()

    else:

        st.info("No Course Outcomes Added")
# ----------------------------
# CO FUNCTIONS
# ----------------------------

def get_all_cos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM co ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_co(statement, bloom):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM co")
    count = cur.fetchone()[0] + 1

    co_no = f"CO{count}"

    cur.execute("""
        INSERT INTO co(co_no, co_statement, bloom_level)
        VALUES (?, ?, ?)
    """, (co_no, statement, bloom))

    conn.commit()
    conn.close()


def delete_co(co_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM co WHERE id=?", (co_id,))

    conn.commit()
    conn.close()