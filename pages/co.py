import streamlit as st
import pandas as pd

from database import (
    get_all_cos,
    add_co,
    delete_co
)


def show():

    st.subheader("🎯 Course Outcomes")

    # -----------------------------
    # Add CO
    # -----------------------------

    with st.expander("➕ Add New Course Outcome"):

        statement = st.text_area(
            "Course Outcome",
            height=100
        )

        bloom = st.selectbox(
            "Bloom's Level",
            ["L1", "L2", "L3", "L4", "L5", "L6"]
        )

        if st.button("Add CO"):

            if statement.strip() == "":
                st.warning("Enter Course Outcome")
            else:
                add_co(statement, bloom)
                st.success("Course Outcome Added")
                st.rerun()

    st.divider()

    # -----------------------------
    # Display COs
    # -----------------------------

    cos = get_all_cos()

    if len(cos) == 0:

        st.info("No Course Outcomes Available")

        return

    df = pd.DataFrame(cos)

    st.dataframe(
        df[["co_no", "co_statement", "bloom_level"]],
        use_container_width=True,
        hide_index=True
    )

    st.write(f"**Total COs : {len(df)}**")

    st.divider()

    # -----------------------------
    # Delete CO
    # -----------------------------

    selected = st.selectbox(
        "Delete Course Outcome",
        df["co_no"]
    )

    if st.button("Delete Selected"):

        co_id = df[df["co_no"] == selected]["id"].values[0]

        delete_co(int(co_id))

        st.success("Deleted Successfully")

        st.rerun()