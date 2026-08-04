"""
Program Outcomes Module
OBE Analytics Pro v1.0.0
"""

import pandas as pd
import streamlit as st

from database import get_all_pos


def show_po():

    st.header("🎓 Program Outcomes (POs)")

    st.write(
        "NBA Program Outcomes (PO1 - PO12)"
    )

    rows = get_all_pos()

    data = []

    for row in rows:

        data.append(
            {
                "PO No": row["po_no"],
                "Program Outcome": row["po_statement"],
            }
        )

    df = pd.DataFrame(data)

    search = st.text_input(
        "🔍 Search Program Outcome",
        placeholder="Type keyword..."
    )

    if search.strip():

        df = df[
            df["Program Outcome"]
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.success(
        f"Total Program Outcomes : {len(df)}"
    )