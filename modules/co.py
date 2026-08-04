import streamlit as st
import pandas as pd

from database import (
    get_all_cos,
    save_all_cos
)

import config


def show_co():
    st.header("🎯 Course Outcomes (COs)")

    st.write("Create and manage Course Outcomes.")

    # ------------------------------------
    # Load Existing COs
    # ------------------------------------

    rows = get_all_cos()

    if rows:

        data = []

        for row in rows:

            data.append({
                "CO No": row["co_no"],
                "Course Outcome": row["co_statement"],
                "Bloom Level": row["bloom_level"]
            })

    else:

        data = [
            {
                "CO No": f"CO{i}",
                "Course Outcome": "",
                "Bloom Level": "L3"
            }
            for i in range(1, 6)
        ]

    df = pd.DataFrame(data)

    # ------------------------------------
    # Editable Table
    # ------------------------------------

    edited_df = st.data_editor(

        df,

        use_container_width=True,

        num_rows="dynamic",

        hide_index=True,

        column_config={

            "CO No": st.column_config.TextColumn(
                "CO No",
                disabled=True
            ),

            "Course Outcome": st.column_config.TextColumn(
                "Course Outcome",
                width="large"
            ),

            "Bloom Level": st.column_config.SelectboxColumn(
                "Bloom Level",
                options=config.BLOOM_LEVELS
            )

        }

    )

    st.divider()

    # ------------------------------------
    # Save
    # ------------------------------------

    if st.button("💾 Save All COs", use_container_width=True):

        save_data = []

        count = 1

        for _, row in edited_df.iterrows():

            statement = " ".join(
                str(row["Course Outcome"]).split()
            )

            if statement == "":
                continue

            save_data.append(
                (
                    f"CO{count}",
                    statement,
                    row["Bloom Level"]
                )
            )

            count += 1

        if len(save_data) == 0:
            st.warning("Please enter at least one Course Outcome.")
            return

        save_all_cos(save_data)

        st.success("Course Outcomes saved successfully.")

        st.rerun()