"""
------------------------------------------------------------
OBE Analytics Pro v1.2 RC1
Module : 08_CO_Attainment.py
Purpose : Course Outcome (CO) Attainment
------------------------------------------------------------
"""

import streamlit as st
import pandas as pd

from database.connection import get_connection
from database.course import get_course

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="CO Attainment",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Course Outcome (CO) Attainment")
st.caption("Direct CO Attainment Calculation")

# ---------------------------------------------------------
# Current Course
# ---------------------------------------------------------

course = get_course()

if course is None:
    st.warning("Please create/select a course first.")
    st.stop()

course_code = course[0]

st.info(f"Selected Course : {course_code}")

# ---------------------------------------------------------
# Load CO Distribution
# ---------------------------------------------------------

conn = get_connection()

co_df = pd.read_sql_query(
    """
    SELECT
        co_no,
        SUM(allocated_marks) AS max_marks
    FROM co_distribution
    WHERE course_code=?
    GROUP BY co_no
    ORDER BY co_no
    """,
    conn,
    params=(course_code,)
)

# ---------------------------------------------------------
# Load Student Marks
# ---------------------------------------------------------

marks_df = pd.read_sql_query(
    """
    SELECT
        reg_no,
        le,
        s1,
        s2
    FROM student_marks
    WHERE course_code=?
    ORDER BY reg_no
    """,
    conn,
    params=(course_code,)
)

if co_df.empty:
    st.error("CO Distribution not available.")
    conn.close()
    st.stop()

if marks_df.empty:
    st.error("Student Marks not available.")
    conn.close()
    st.stop()

# ---------------------------------------------------------
# Display Input Data
# ---------------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("CO Distribution")

    st.dataframe(
        co_df,
        use_container_width=True,
        hide_index=True
    )

with right:

    st.subheader("Student Marks")

    st.dataframe(
        marks_df,
        use_container_width=True,
        hide_index=True
    )

st.divider()

calculate = st.button(
    "📊 Calculate CO Attainment",
    use_container_width=True,
    key="calculate_co_attainment"
)

# ---------------------------------------------------------
# CO Attainment Calculation
# ---------------------------------------------------------

if calculate:

    total_students = len(marks_df)

    results = []

    for _, co in co_df.iterrows():

        co_no = co["co_no"]

        max_marks = float(co["max_marks"])

        target_marks = 0.60 * max_marks

        qualified = 0

        for _, student in marks_df.iterrows():

            obtained = (
                float(student["le"] or 0)
                + float(student["s1"] or 0)
                + float(student["s2"] or 0)
            )

            if obtained >= target_marks:
                qualified += 1

        attainment_percent = (
            qualified / total_students
        ) * 100

        if attainment_percent >= 70:
            level = 3
        elif attainment_percent >= 60:
            level = 2
        else:
            level = 1

        results.append(
            {
                "CO": co_no,
                "Maximum Marks": round(max_marks, 2),
                "Target Marks": round(target_marks, 2),
                "Qualified Students": qualified,
                "Total Students": total_students,
                "Attainment %": round(attainment_percent, 2),
                "Direct Level": level,
            }
        )

    result_df = pd.DataFrame(results)
        # ---------------------------------------------------------
    # Save Results to Database
    # ---------------------------------------------------------

    cur = conn.cursor()

    # Remove previous calculations
    cur.execute(
        "DELETE FROM direct_attainment WHERE course_code=?",
        (course_code,)
    )

    cur.execute(
        "DELETE FROM final_co_attainment WHERE course_code=?",
        (course_code,)
    )

    # Save each CO
    for _, row in result_df.iterrows():

        co = row["CO"]
        level = int(row["Direct Level"])

        # Direct Attainment
        cur.execute(
            """
            INSERT INTO direct_attainment
            (
                course_code,
                co_no,
                attainment
            )
            VALUES (?, ?, ?)
            """,
            (
                course_code,
                co,
                level
            )
        )

        # Final CO Attainment
        # (Temporary: Survey = Direct)
        cur.execute(
            """
            INSERT INTO final_co_attainment
            (
                course_code,
                co_no,
                direct,
                survey,
                final
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                course_code,
                co,
                level,
                level,
                level
            )
        )

    conn.commit()

    # ---------------------------------------------------------
    # Display Results
    # ---------------------------------------------------------

    st.success("CO Attainment calculated successfully.")

    st.subheader("CO Attainment Results")

    st.dataframe(
        result_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Total COs",
            len(result_df)
        )

    with c2:
        st.metric(
            "Average Direct Level",
            round(
                result_df["Direct Level"].mean(),
                2
            )
        )

    with c3:
        st.metric(
            "Average Attainment %",
            f"{result_df['Attainment %'].mean():.2f}%"
        )

    st.divider()

    st.subheader("Direct CO Attainment")

    chart_df = result_df[
        ["CO", "Direct Level"]
    ]

    st.bar_chart(
        chart_df.set_index("CO")
    )

    conn.close()

