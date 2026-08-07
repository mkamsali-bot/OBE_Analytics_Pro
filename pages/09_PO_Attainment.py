"""
------------------------------------------------------------
OBE Analytics Pro v1.2 RC3
Module : 09_PO_Attainment.py
Purpose : Programme Outcome (PO) Attainment
------------------------------------------------------------
"""

import pandas as pd
import streamlit as st
import plotly.express as px

from database.connection import get_connection

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="PO Attainment",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Programme Outcome (PO) Attainment")
st.caption("Programme Outcome Attainment using Final CO Attainment")

# ---------------------------------------------------------
# Database Connection
# ---------------------------------------------------------

conn = get_connection()

# ---------------------------------------------------------
# Load Available Courses
# ---------------------------------------------------------

@st.cache_data
def load_courses():

    query = """
    SELECT DISTINCT course_code
    FROM final_co_attainment
    ORDER BY course_code
    """

    return pd.read_sql_query(query, conn)

courses = load_courses()

if courses.empty:

    st.warning("No CO Attainment data available.")

    st.stop()

# ---------------------------------------------------------
# Course Selection
# ---------------------------------------------------------

course_code = st.selectbox(
    "Select Course",
    courses["course_code"].tolist(),
    key="po_course"
)

st.success(f"Selected Course : {course_code}")

st.divider()
# ---------------------------------------------------------
# Load Final CO Attainment
# ---------------------------------------------------------

@st.cache_data
def load_final_co(course_code):

    query = """
    SELECT
        co_no,
        direct,
        survey,
        final
    FROM final_co_attainment
    WHERE course_code = ?
    ORDER BY co_no
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(course_code,)
    )

    # Standardize CO names
    df["co_no"] = (
        df["co_no"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return df


# ---------------------------------------------------------
# Load CO-PO Mapping
# ---------------------------------------------------------

@st.cache_data
def load_mapping(course_code):

    query = """
    SELECT
        co_no,
        po_no,
        level
    FROM co_po_mapping
    WHERE course_code = ?
    ORDER BY co_no, po_no
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(course_code,)
    )

    # Standardize CO names
    df["co_no"] = (
        df["co_no"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return df


# ---------------------------------------------------------
# Read Data
# ---------------------------------------------------------

co_df = load_final_co(course_code)
mapping_df = load_mapping(course_code)

# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

if co_df.empty:

    st.error("Final CO Attainment not found.")
    st.stop()

if mapping_df.empty:

    st.error("CO-PO Mapping not found.")
    st.stop()

# ---------------------------------------------------------
# Display Data
# ---------------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    st.subheader("Final CO Attainment")

    st.dataframe(
        co_df,
        use_container_width=True,
        hide_index=True
    )

with col2:

    st.subheader("CO-PO Mapping")

    st.dataframe(
        mapping_df,
        use_container_width=True,
        hide_index=True
    )

st.divider()

calculate = st.button(
    "📊 Calculate PO Attainment",
    use_container_width=True,
    key="calculate_po"
)
# ---------------------------------------------------------
# Calculate PO Attainment
# ---------------------------------------------------------

if calculate:

    # Merge CO Attainment with CO-PO Mapping
    merged_df = pd.merge(
        mapping_df,
        co_df,
        on="co_no",
        how="inner"
    )

    if merged_df.empty:

        st.error("No matching CO-PO records found.")
        st.stop()

    # ---------------------------------------------
    # Calculate Weighted PO Attainment
    # ---------------------------------------------

    po_results = []

    for po in sorted(merged_df["po_no"].unique()):

        po_data = merged_df[
            merged_df["po_no"] == po
        ]

        weighted_sum = (
            po_data["final"] *
            po_data["level"]
        ).sum()

        total_weight = (
            po_data["level"]
        ).sum()

        if total_weight == 0:
            attainment = 0.0
        else:
            attainment = round(
                weighted_sum / total_weight,
                3
            )

        po_results.append(
            {
                "PO": po,
                "Mapped COs": len(po_data),
                "Weight": int(total_weight),
                "PO Attainment": attainment
            }
        )

    po_df = pd.DataFrame(po_results)

    st.success("PO Attainment calculated successfully.")

    st.subheader("Programme Outcome Attainment")

    st.dataframe(
        po_df,
        use_container_width=True,
        hide_index=True
    )

    st.session_state["po_df"] = po_df
        # ---------------------------------------------------------
    # Summary Metrics
    # ---------------------------------------------------------

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Total POs",
            len(po_df)
        )

    with c2:
        st.metric(
            "Average PO Attainment",
            round(
                po_df["PO Attainment"].mean(),
                2
            )
        )

    with c3:
        st.metric(
            "Maximum PO Attainment",
            round(
                po_df["PO Attainment"].max(),
                2
            )
        )

    # ---------------------------------------------------------
    # Bar Chart
    # ---------------------------------------------------------

    st.subheader("PO Attainment Chart")

    fig = px.bar(
        po_df,
        x="PO",
        y="PO Attainment",
        text="PO Attainment",
        color="PO Attainment",
        title="Programme Outcome Attainment"
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        height=500,
        xaxis_title="Programme Outcomes",
        yaxis_title="Attainment Level"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ---------------------------------------------------------
    # Save to Database
    # ---------------------------------------------------------

    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM po_attainment
        WHERE course_code=?
        """,
        (course_code,)
    )

    for _, row in po_df.iterrows():

        cur.execute(
            """
            INSERT INTO po_attainment
            (
                course_code,
                po_no,
                attainment
            )
            VALUES (?, ?, ?)
            """,
            (
                course_code,
                row["PO"],
                float(row["PO Attainment"])
            )
        )

    conn.commit()

    st.success("PO Attainment saved successfully.")

# ---------------------------------------------------------
# Download Results
# ---------------------------------------------------------

st.divider()

# CSV Download
csv = po_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "📄 Download CSV",
    data=csv,
    file_name=f"{course_code}_PO_Attainment.csv",
    mime="text/csv",
    use_container_width=True
)

# Excel Download

with open("temp_po_attainment.xlsx", "rb") as f:

    st.download_button(
        "📊 Download Excel",
        data=f,
        file_name=f"{course_code}_PO_Attainment.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

conn.close()