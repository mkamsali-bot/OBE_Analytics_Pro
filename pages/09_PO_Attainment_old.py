"""
------------------------------------------------------------
OBE Analytics Pro v1.2 RC1
Module : 09_PO_Attainment.py
Purpose: Calculate Programme Outcome (PO) Attainment
Author : OpenAI
------------------------------------------------------------
"""

import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="PO Attainment",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 PO Attainment")
st.caption("Direct (80%) + Indirect (20%) Programme Outcome Attainment")

# ---------------------------------------------------------
# Database Connection
# ---------------------------------------------------------

conn = sqlite3.connect("database/obe.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

@st.cache_data
def load_courses():
    query = """
    SELECT id,
           course_code,
           course_name,
           academic_year,
           semester,
           faculty_name
    FROM course_master
    ORDER BY course_code
    """
    return pd.read_sql_query(query, conn)


@st.cache_data
def load_co_attainment(course_id):
    query = """
    SELECT co,
           attainment
    FROM co_attainment
    WHERE course_id=?
    ORDER BY co
    """
    return pd.read_sql_query(query, conn, params=(course_id,))


@st.cache_data
def load_mapping(course_id):
    query = """
    SELECT *
    FROM co_po_mapping
    WHERE course_id=?
    ORDER BY co
    """
    return pd.read_sql_query(query, conn, params=(course_id,))


# ---------------------------------------------------------
# Course Selection
# ---------------------------------------------------------

courses = load_courses()

if courses.empty:
    st.warning("No courses available.")
    st.stop()

course_display = (
    courses["course_code"] +
    " - " +
    courses["course_name"]
)

selected = st.selectbox(
    "Select Course",
    course_display
)

course = courses.iloc[course_display.tolist().index(selected)]

course_id = int(course["id"])

# ---------------------------------------------------------
# Course Information
# ---------------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Course Code", course["course_code"])

with c2:
    st.metric("Academic Year", course["academic_year"])

with c3:
    st.metric("Semester", course["semester"])

with c4:
    st.metric("Faculty", course["faculty_name"])

st.divider()

# ---------------------------------------------------------
# Load CO Attainment
# ---------------------------------------------------------

co_df = load_co_attainment(course_id)

if co_df.empty:
    st.error("CO Attainment has not yet been calculated.")
    st.stop()

st.subheader("CO Attainment")

st.dataframe(
    co_df,
    use_container_width=True,
    hide_index=True
)

# ---------------------------------------------------------
# Load CO-PO Mapping
# ---------------------------------------------------------

mapping_df = load_mapping(course_id)

if mapping_df.empty:
    st.error("CO-PO Mapping not available.")
    st.stop()

st.subheader("CO-PO Mapping")

st.dataframe(
    mapping_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

calculate = st.button(
    "📊 Calculate Direct PO Attainment",
    use_container_width=True
)

# ---------------------------------------------------------
# Calculate Direct PO Attainment
# ---------------------------------------------------------

if calculate:

    # Merge CO Attainment with CO-PO Mapping
    merged_df = pd.merge(
        co_df,
        mapping_df,
        on="co",
        how="inner"
    )

    if merged_df.empty:
        st.error("Unable to merge CO Attainment with CO-PO Mapping.")
        st.stop()

    po_columns = [
        col for col in merged_df.columns
        if col.upper().startswith("PO")
    ]

    direct_results = []

    for po in po_columns:

        numerator = 0.0
        denominator = 0.0

        for _, row in merged_df.iterrows():

            mapping = row[po]

            if pd.isna(mapping):
                continue

            mapping = float(mapping)

            if mapping == 0:
                continue

            attainment = float(row["attainment"])

            numerator += attainment * mapping
            denominator += mapping

        if denominator == 0:
            direct = 0
        else:
            direct = round(numerator / denominator, 3)

        direct_results.append(
            {
                "PO": po,
                "Direct Attainment": direct
            }
        )

    direct_df = pd.DataFrame(direct_results)

    st.success("Direct PO Attainment calculated successfully.")

    st.subheader("Direct PO Attainment")

    st.dataframe(
        direct_df,
        use_container_width=True,
        hide_index=True
    )

    # ---------------------------------------------------------
    # Summary Metrics
    # ---------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "POs Calculated",
            len(direct_df)
        )

    with c2:
        st.metric(
            "Average Direct Attainment",
            round(direct_df["Direct Attainment"].mean(), 2)
        )

    with c3:
        st.metric(
            "Highest Attainment",
            round(direct_df["Direct Attainment"].max(), 2)
        )

    # ---------------------------------------------------------
    # Bar Chart
    # ---------------------------------------------------------

    fig = px.bar(
        direct_df,
        x="PO",
        y="Direct Attainment",
        text="Direct Attainment",
        title="Direct PO Attainment"
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        height=500,
        yaxis_title="Attainment Level",
        xaxis_title="Programme Outcomes"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # Store in session for next step
    st.session_state["direct_po_df"] = direct_df

    # ---------------------------------------------------------
# Part 3 : Indirect PO Attainment (Course Exit Survey)
# ---------------------------------------------------------

st.divider()
st.subheader("📝 Indirect PO Attainment (Course Exit Survey)")

st.info(
    "Enter the indirect attainment values (0–3) obtained from the Course Exit Survey. "
    "These values contribute 20% towards the final PO attainment."
)

# Create editable dataframe
indirect_df = direct_df.copy()
indirect_df["Indirect Attainment"] = 0.0

edited_df = st.data_editor(
    indirect_df,
    use_container_width=True,
    hide_index=True,
    num_rows="fixed",
    column_config={
        "PO": st.column_config.TextColumn(
            "Programme Outcome",
            disabled=True
        ),
        "Direct Attainment": st.column_config.NumberColumn(
            "Direct Attainment",
            format="%.3f",
            disabled=True
        ),
        "Indirect Attainment": st.column_config.NumberColumn(
            "Indirect Attainment",
            min_value=0.0,
            max_value=3.0,
            step=0.01,
            format="%.3f"
        )
    }
)

# ---------------------------------------------------------
# Validate Indirect Values
# ---------------------------------------------------------

invalid = edited_df[
    (edited_df["Indirect Attainment"] < 0) |
    (edited_df["Indirect Attainment"] > 3)
]

if not invalid.empty:
    st.error("Indirect attainment values must be between 0.0 and 3.0.")
    st.stop()

# Store for next part
st.session_state["po_indirect_df"] = edited_df

st.success("Indirect attainment values are ready.")

# Preview
st.subheader("Preview")

st.dataframe(
    edited_df,
    use_container_width=True,
    hide_index=True
)

# Continue button
calculate_final = st.button(
    "✅ Calculate Final PO Attainment",
    use_container_width=True
)

# ---------------------------------------------------------
# Part 4 : Final PO Attainment (80% Direct + 20% Indirect)
# ---------------------------------------------------------

if calculate_final:

    if "po_indirect_df" not in st.session_state:
        st.error("Indirect attainment data not found.")
        st.stop()

    final_df = st.session_state["po_indirect_df"].copy()

    # -----------------------------------------------------
    # Final PO Attainment
    # -----------------------------------------------------

    final_df["Final Attainment"] = (
        final_df["Direct Attainment"] * 0.80
        + final_df["Indirect Attainment"] * 0.20
    ).round(3)

    st.success("Final PO Attainment calculated successfully.")

    st.subheader("🎯 Final PO Attainment")

    st.dataframe(
        final_df,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------------------
    # Summary Metrics
    # -----------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Average Final Attainment",
            round(final_df["Final Attainment"].mean(), 2)
        )

    with col2:
        st.metric(
            "Highest Final Attainment",
            round(final_df["Final Attainment"].max(), 2)
        )

    with col3:
        st.metric(
            "Lowest Final Attainment",
            round(final_df["Final Attainment"].min(), 2)
        )

    # -----------------------------------------------------
    # Comparison Chart
    # -----------------------------------------------------

    chart_df = final_df.melt(
        id_vars="PO",
        value_vars=[
            "Direct Attainment",
            "Indirect Attainment",
            "Final Attainment"
        ],
        var_name="Type",
        value_name="Attainment"
    )

    fig = px.bar(
        chart_df,
        x="PO",
        y="Attainment",
        color="Type",
        barmode="group",
        text="Attainment",
        title="PO Attainment Comparison"
    )

    fig.update_traces(texttemplate="%{text:.2f}")

    fig.update_layout(
        height=550,
        xaxis_title="Programme Outcomes",
        yaxis_title="Attainment Level",
        legend_title=""
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # -----------------------------------------------------
    # Final Attainment Chart
    # -----------------------------------------------------

    fig2 = px.bar(
        final_df,
        x="PO",
        y="Final Attainment",
        text="Final Attainment",
        title="Final PO Attainment"
    )

    fig2.update_traces(
        textposition="outside"
    )

    fig2.update_layout(
        height=500,
        xaxis_title="Programme Outcomes",
        yaxis_title="Final Attainment"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # -----------------------------------------------------
    # Store for Database Saving
    # -----------------------------------------------------

    st.session_state["final_po_df"] = final_df

    st.success("Final PO Attainment is ready to be saved.")

    # ---------------------------------------------------------
# Part 5 : Save PO Attainment & Export Results
# ---------------------------------------------------------

if "final_po_df" in st.session_state:

    final_df = st.session_state["final_po_df"]

    st.divider()
    st.subheader("💾 Save & Export")

    col1, col2 = st.columns(2)

    # -----------------------------------------------------
    # Save to Database
    # -----------------------------------------------------

    with col1:

        if st.button(
            "💾 Save PO Attainment",
            use_container_width=True
        ):

            try:

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS po_attainment(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        academic_year TEXT,
                        semester TEXT,
                        course_id INTEGER,
                        po TEXT,
                        direct_attainment REAL,
                        indirect_attainment REAL,
                        final_attainment REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(academic_year, semester, course_id, po)
                    )
                """)

                conn.commit()

                for _, row in final_df.iterrows():

                    cursor.execute("""
                        INSERT OR REPLACE INTO po_attainment
                        (
                            academic_year,
                            semester,
                            course_id,
                            po,
                            direct_attainment,
                            indirect_attainment,
                            final_attainment
                        )
                        VALUES
                        (
                            ?,?,?,?,?,?,?
                        )
                    """,
                    (
                        course["academic_year"],
                        course["semester"],
                        course_id,
                        row["PO"],
                        float(row["Direct Attainment"]),
                        float(row["Indirect Attainment"]),
                        float(row["Final Attainment"])
                    ))

                conn.commit()

                st.success("✅ PO Attainment saved successfully.")

            except Exception as e:

                st.error(f"Database Error : {e}")

    # -----------------------------------------------------
    # Export CSV
    # -----------------------------------------------------

    with col2:

        csv = final_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "⬇ Download CSV",
            csv,
            file_name=f"{course['course_code']}_PO_Attainment.csv",
            mime="text/csv",
            use_container_width=True
        )

    # -----------------------------------------------------
    # Export Excel
    # -----------------------------------------------------

    from io import BytesIO

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        final_df.to_excel(
            writer,
            sheet_name="PO Attainment",
            index=False
        )

    excel_data = output.getvalue()

    st.download_button(
        "📥 Download Excel",
        excel_data,
        file_name=f"{course['course_code']}_PO_Attainment.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    # -----------------------------------------------------
    # Display Final Report
    # -----------------------------------------------------

    st.divider()

    st.subheader("📋 Final PO Attainment Report")

    report = final_df.copy()

    report.rename(
        columns={
            "PO": "Programme Outcome",
            "Direct Attainment": "Direct (80%)",
            "Indirect Attainment": "Indirect (20%)",
            "Final Attainment": "Final PO Attainment"
        },
        inplace=True
    )

    st.dataframe(
        report,
        use_container_width=True,
        hide_index=True
    )

    st.success("🎉 PO Attainment module completed successfully.")