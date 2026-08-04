"""
CO-PO Mapping Module
OBE Analytics Pro v1.0.0
"""

import pandas as pd
import streamlit as st

from database import (
    get_all_cos,
    get_all_pos,
    get_mapping,
    save_mapping,
)


def load_mapping_matrix():

    cos = get_all_cos()
    pos = get_all_pos()

    if len(cos) == 0:
        return pd.DataFrame()

    data = []

    for co in cos:

        row = {"CO": co["co_no"]}

        for po in pos:
            row[po["po_no"]] = 0

        data.append(row)

    df = pd.DataFrame(data)

    mappings = get_mapping()

    for m in mappings:

        df.loc[
            df["CO"] == m["co_no"],
            m["po_no"]
        ] = m["level"]

    return df      # ← This line MUST exist


def save_mapping_matrix(df):
    """
    Save CO-PO Mapping Matrix
    """

    save_data = []

    po_columns = [col for col in df.columns if col != "CO"]

    for _, row in df.iterrows():

        co = row["CO"]

        for po in po_columns:

            level = int(row[po])

            # Save only non-zero mappings
            if level > 0:
                save_data.append(
                    (
                        co,
                        po,
                        level
                    )
                )

    save_mapping(save_data)
    return load_mapping_matrix()

def show_mapping():

    st.header("🔗 CO–PO Mapping")

    st.write(
        "Map Course Outcomes (COs) with Program Outcomes (POs)."
    )

    df = load_mapping_matrix()

    if df.empty:

        st.warning("Please create Course Outcomes first.")

        return
    column_config = {}

    for col in df.columns:

        if col == "CO":

            column_config[col] = st.column_config.TextColumn(
                col,
                disabled=True
            )

        else:

            column_config[col] = st.column_config.SelectboxColumn(
                col,
                options=[0, 1, 2, 3],
                width="small"
            )

    edited_df = st.data_editor(

        df,

        hide_index=True,

        use_container_width=True,

        column_config=column_config

    )

    st.divider()

    if st.button(
        "💾 Save Mapping",
        use_container_width=True
    ):

        save_mapping_matrix(edited_df)

        st.success(
            "CO–PO Mapping saved successfully."
        )

        st.rerun()