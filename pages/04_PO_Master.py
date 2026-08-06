"""
PO Master
OBE Analytics Pro v1.1.2
"""

import streamlit as st
import pandas as pd

from database import (
    preload_pos,
    get_all_pos,
)

# ---------------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------------

st.title("📙 Program Outcomes")
st.caption("NBA Program Outcomes")

# ---------------------------------------------------------
# LOAD DEFAULT POs
# ---------------------------------------------------------

preload_pos()

rows = get_all_pos()

df = pd.DataFrame(
    rows,
    columns=[
        "PO No",
        "Program Outcome"
    ]
)

# ---------------------------------------------------------
# DISPLAY
# ---------------------------------------------------------

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.metric(
    "Total Program Outcomes",
    len(df)
)