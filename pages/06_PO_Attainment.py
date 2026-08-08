"""
OBE Analytics - Simple Edition
06_PO_Attainment.py

PO Attainment:
1. Uses saved CO attainment from the CO Attainment module.
2. Uses saved CO-PO mapping levels (1=Low, 2=Moderate, 3=High).
3. Calculates Direct PO Attainment as a weighted average of CO attainment.
4. Allows manual Course Survey / Indirect PO Attainment.
5. Final PO = 80% Direct + 20% Indirect.
6. Saves PO attainment to po_attainment.
7. Calculates PSO attainment separately from CO-PSO mapping.
"""

import streamlit as st
import pandas as pd

from database import (
    get_active_course,
    fetch_all,
    fetch_dataframe,
    execute_query
)


# --------------------------------------------------------
# Page Configuration
# --------------------------------------------------------

st.set_page_config(
    page_title="PO Attainment",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 PO Attainment")
st.caption(
    "PO Attainment from CO-wise marks and CO-PO mapping"
)
st.divider()


# --------------------------------------------------------
# Active Course
# --------------------------------------------------------

course = get_active_course()

if course is None:
    st.warning(
        "Please select an Active Course from Course Management."
    )
    st.stop()

course_id = course["id"]


# --------------------------------------------------------
# PO Attainment Settings
# --------------------------------------------------------

st.subheader("⚙️ PO Attainment Settings")

current_use_indirect = bool(
    course["use_indirect"]
)

current_direct_weight = float(
    course["direct_weight"] or 0
)

current_indirect_weight = float(
    course["indirect_weight"] or 0
)

if current_use_indirect:
    st.success(
        f"Indirect attainment is enabled: "
        f"{current_direct_weight:.0f}% Direct + "
        f"{current_indirect_weight:.0f}% Indirect."
    )
else:
    st.warning(
        "Indirect attainment is currently disabled for this course."
    )

if st.button(
    "🔧 Enable Indirect Attainment (80% Direct + 20% Indirect)",
    type="primary",
    key="enable_indirect_80_20"
):
    try:
        execute_query(
            """
            UPDATE course
            SET
                use_indirect=1,
                direct_weight=80,
                indirect_weight=20
            WHERE id=?
            """,
            (course_id,)
        )

        st.success(
            "✅ Indirect attainment enabled successfully: "
            "80% Direct + 20% Indirect."
        )

        st.rerun()

    except Exception as e:
        st.error(
            "Unable to update PO attainment settings."
        )
        st.exception(e)

st.divider()


st.success(
    f"""
### Active Course

**Course Code:** {course["course_code"]}

**Course Name:** {course["course_name"]}

**Faculty:** {course["faculty"]}

**Semester:** {course["semester"]}

**Academic Year:** {course["academic_year"]}
"""
)


# --------------------------------------------------------
# Load COs
# --------------------------------------------------------

cos = fetch_all(
    """
    SELECT
        co_no,
        co_statement,
        bloom_level
    FROM co
    WHERE course_id=?
    ORDER BY CAST(co_no AS INTEGER)
    """,
    (course_id,)
)

if len(cos) != 5:
    st.warning(
        "Please define all 5 Course Outcomes first."
    )
    st.stop()


# --------------------------------------------------------
# Load Students
# --------------------------------------------------------

students = fetch_dataframe(
    """
    SELECT
        student_id,
        student_name,
        ce,
        s1,
        s2
    FROM marks
    WHERE course_id=?
    ORDER BY student_id
    """,
    (course_id,)
)

if students.empty:
    st.warning(
        "No student marks are available for this course."
    )
    st.stop()

st.info(
    f"Student records available: {len(students)}"
)


# --------------------------------------------------------
# Load CO Marks
# --------------------------------------------------------

co_marks_df = fetch_dataframe(
    """
    SELECT
        student_id,
        co_no,
        marks
    FROM co_marks
    WHERE course_id=?
    ORDER BY student_id, co_no
    """,
    (course_id,)
)

if co_marks_df.empty:
    st.error(
        "No CO-wise marks are available. "
        "Please generate CO marks in 05_CO_Attainment first."
    )
    st.stop()


# ========================================================
# CALCULATE CO ATTAINMENT DIRECTLY FROM CO MARKS
# ========================================================

st.divider()
st.subheader("Final CO Attainment")

st.info(
    "CO attainment is taken from the validated CO Attainment module. "
    "This PO Attainment module does not recalculate CO attainment."
)

saved_co_attainment = fetch_dataframe(
    """
    SELECT
        co_no,
        attainment
    FROM co_attainment
    WHERE course_id=?
    ORDER BY co_no
    """,
    (course_id,)
)

if saved_co_attainment.empty:
    st.error(
        "No saved CO Attainment is available. "
        "Please calculate and save CO Attainment first."
    )
    st.stop()

co_results = []

for co in cos:

    co_no = int(co["co_no"])

    matching = saved_co_attainment[
        saved_co_attainment["co_no"].astype(str).str.upper()
        == f"CO{co_no}"
    ]

    if matching.empty:
        matching = saved_co_attainment[
            saved_co_attainment["co_no"].astype(str).str.strip()
            == str(co_no)
        ]

    attainment = (
        float(matching.iloc[0]["attainment"])
        if not matching.empty
        else 0.0
    )

    co_results.append(
        {
            "CO": f"CO{co_no}",
            "CO Attainment (%)": round(attainment, 2),
        }
    )


co_attainment_df = pd.DataFrame(
    co_results
)

st.dataframe(
    co_attainment_df,
    use_container_width=True,
    hide_index=True
)

st.success(
    "✅ Final CO Attainment calculated successfully."
)


# --------------------------------------------------------
# CO Attainment
# --------------------------------------------------------

st.info(
    "CO Attainment is calculated and saved in 05_CO_Attainment.py. "
    "This module uses those saved values and does not recalculate "
    "or overwrite CO Attainment."
)


# ========================================================
# CO-PO MAPPING
# ========================================================

st.divider()
st.subheader("CO–PO Mapping")

mapping_df = fetch_dataframe(
    """
    SELECT
        co_no,
        po_no,
        mapping_level
    FROM mapping
    WHERE course_id=?
    AND mapping_level > 0
    """,
    (course_id,)
)

if mapping_df.empty:
    st.error(
        "No CO–PO mapping found. "
        "Please save the CO–PO mapping first."
    )
    st.stop()


mapping_df["co_no"] = (
    mapping_df["co_no"]
    .astype(str)
    .str.strip()
)

mapping_df["po_no"] = (
    mapping_df["po_no"]
    .astype(str)
    .str.strip()
    .str.upper()
)

mapping_df["mapping_level"] = pd.to_numeric(
    mapping_df["mapping_level"],
    errors="coerce"
).fillna(0.0)


mapping_display = mapping_df.copy()

mapping_display["CO"] = mapping_display[
    "co_no"
].apply(
    lambda x: x if x.upper().startswith("CO")
    else f"CO{x}"
)

mapping_display = mapping_display[
    [
        "CO",
        "po_no",
        "mapping_level"
    ]
].rename(
    columns={
        "po_no": "PO",
        "mapping_level": "Mapping Level"
    }
)

st.dataframe(
    mapping_display,
    use_container_width=True,
    hide_index=True
)


# ========================================================
# DIRECT PO ATTAINMENT
# ========================================================

st.divider()
st.subheader("📊 Direct PO Attainment")

# Prepare CO attainment for mapping.
co_for_mapping = co_attainment_df.copy()

co_for_mapping["co_no"] = (
    co_for_mapping["CO"]
    .str.replace(
        "CO",
        "",
        regex=False
    )
    .str.strip()
)

co_for_mapping["attainment"] = pd.to_numeric(
    co_for_mapping[
        "CO Attainment (%)"
    ],
    errors="coerce"
).fillna(0.0)


merged = pd.merge(
    mapping_df,
    co_for_mapping[
        [
            "co_no",
            "attainment"
        ]
    ],
    on="co_no",
    how="inner"
)

if merged.empty:

    st.error(
        "Unable to match CO Attainment with CO–PO Mapping."
    )
    st.stop()


po_results = []

po_values = sorted(
    merged["po_no"].unique(),
    key=lambda value: int(
        str(value).replace(
            "PO",
            ""
        )
    )
)


for po_no in po_values:

    po_data = merged[
        merged["po_no"] == po_no
    ].copy()

    weighted_sum = (
        po_data["attainment"]
        * po_data["mapping_level"]
    ).sum()

    total_weight = (
        po_data["mapping_level"]
    ).sum()

    direct_value = (
        weighted_sum / total_weight
        if total_weight > 0
        else 0.0
    )

    po_results.append(
        {
            "PO": po_no,
            "Mapped COs": len(po_data),
            "Mapping Weight": round(
                float(total_weight),
                2
            ),
            "Direct Attainment (%)": round(
                float(direct_value),
                2
            )
        }
    )


direct_df = pd.DataFrame(
    po_results
)

st.dataframe(
    direct_df,
    use_container_width=True,
    hide_index=True
)


# ========================================================
# INDIRECT ATTAINMENT
# ========================================================

st.divider()
st.subheader("📝 Course Survey / Indirect PO Attainment")

use_indirect = bool(
    course["use_indirect"]
)

direct_weight = (
    float(course["direct_weight"])
    if use_indirect
    else 100.0
)

indirect_weight = (
    float(course["indirect_weight"])
    if use_indirect
    else 0.0
)

if use_indirect:

    st.info(
        f"""
**Direct Weight:** {direct_weight:.0f}%

**Indirect Weight:** {indirect_weight:.0f}%

Final PO = Direct × {direct_weight:.0f}%
+ Course Survey × {indirect_weight:.0f}%
"""
    )

else:

    st.info(
        "Indirect attainment is disabled. "
        "Final PO Attainment equals Direct Attainment."
    )


# --------------------------------------------------------
# Existing Indirect Values
# --------------------------------------------------------

saved_po = fetch_dataframe(
    """
    SELECT
        po_no,
        indirect
    FROM po_attainment
    WHERE course_id=?
    """,
    (course_id,)
)

saved_indirect = {}

if not saved_po.empty:

    for _, row in saved_po.iterrows():

        saved_indirect[
            str(row["po_no"]).upper()
        ] = float(
            row["indirect"] or 0
        )


indirect_values = {}

indirect_cols = st.columns(
    min(
        5,
        max(
            1,
            len(direct_df)
        )
    )
)

for index, row in direct_df.iterrows():

    po_no = str(
        row["PO"]
    ).upper()

    with indirect_cols[
        index % len(indirect_cols)
    ]:

        if use_indirect:

            indirect_values[po_no] = st.number_input(
                f"{po_no} Course Survey (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(
                    saved_indirect.get(
                        po_no,
                        0.0
                    )
                ),
                step=0.5,
                key=f"indirect_{po_no}"
            )

        else:

            indirect_values[po_no] = 0.0


# ========================================================
# FINAL PO ATTAINMENT
# ========================================================

st.divider()
st.subheader("🏆 Final PO Attainment")

final_results = []

for _, row in direct_df.iterrows():

    po_no = str(
        row["PO"]
    ).upper()

    direct_value = float(
        row["Direct Attainment (%)"]
    )

    indirect_value = float(
        indirect_values.get(
            po_no,
            0.0
        )
    )

    final_value = (
        direct_value
        * direct_weight
        / 100.0
        +
        indirect_value
        * indirect_weight
        / 100.0
    )

    final_results.append(
        {
            "PO": po_no,
            "Direct (%)": round(
                direct_value,
                2
            ),
            "Indirect (%)": round(
                indirect_value,
                2
            ),
            "Final PO Attainment (%)": round(
                final_value,
                2
            )
        }
    )


final_df = pd.DataFrame(
    final_results
)

st.dataframe(
    final_df,
    use_container_width=True,
    hide_index=True
)


# ========================================================
# PSO ATTAINMENT
# ========================================================

st.divider()
st.subheader("🎯 PSO Attainment")

st.info(
    "PSO attainment is calculated separately using CO attainment "
    "and the saved CO–PSO mapping. Mapping levels are 1 = Low, "
    "2 = Moderate, 3 = High."
)

pso_mapping_df = fetch_dataframe(
    """
    SELECT
        co_no,
        pso_no,
        mapping_level
    FROM pso_mapping
    WHERE course_id=?
      AND mapping_level > 0
    ORDER BY co_no, pso_no
    """,
    (course_id,)
)

if pso_mapping_df.empty:

    st.warning(
        "No CO–PSO mapping found. "
        "Please save the CO–PSO mapping first."
    )

else:

    pso_mapping_df["co_no"] = (
        pso_mapping_df["co_no"]
        .astype(str)
        .str.replace("CO", "", regex=False)
        .str.strip()
    )

    pso_mapping_df["pso_no"] = (
        pso_mapping_df["pso_no"]
        .astype(str)
        .str.replace("PSO", "", regex=False)
        .str.strip()
    )

    pso_mapping_df["mapping_level"] = pd.to_numeric(
        pso_mapping_df["mapping_level"],
        errors="coerce",
    ).fillna(0.0)

    pso_merged = pd.merge(
        pso_mapping_df,
        co_for_mapping[
            [
                "co_no",
                "attainment",
            ]
        ],
        on="co_no",
        how="inner",
    )

    pso_results = []

    for pso_no in sorted(
        pso_merged["pso_no"].unique(),
        key=lambda value: int(value),
    ):

        pso_data = pso_merged[
            pso_merged["pso_no"] == pso_no
        ].copy()

        weighted_sum = (
            pso_data["attainment"]
            * pso_data["mapping_level"]
        ).sum()

        total_weight = pso_data["mapping_level"].sum()

        pso_value = (
            weighted_sum / total_weight
            if total_weight > 0
            else 0.0
        )

        pso_results.append(
            {
                "PSO": f"PSO{pso_no}",
                "Mapped COs": len(pso_data),
                "Mapping Weight": round(
                    float(total_weight),
                    2,
                ),
                "PSO Attainment (%)": round(
                    float(pso_value),
                    2,
                ),
            }
        )

    pso_df = pd.DataFrame(pso_results)

    st.dataframe(
        pso_df,
        use_container_width=True,
        hide_index=True,
    )

# --------------------------------------------------------
# Save PO Attainment
# --------------------------------------------------------

st.divider()

if st.button(
    "💾 Save PO Attainment",
    type="primary",
    use_container_width=True,
    key="save_po_attainment"
):

    try:

        # Save PSO attainment separately when CO–PSO mapping exists.
        if "pso_df" in locals() and not pso_df.empty:

            execute_query(
                """
                CREATE TABLE IF NOT EXISTS pso_attainment(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id INTEGER NOT NULL,
                    pso_no TEXT NOT NULL,
                    attainment REAL DEFAULT 0
                )
                """
            )

            execute_query(
                """
                DELETE FROM pso_attainment
                WHERE course_id=?
                """,
                (course_id,)
            )

            for _, pso_row in pso_df.iterrows():

                execute_query(
                    """
                    INSERT INTO pso_attainment(
                        course_id,
                        pso_no,
                        attainment
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        course_id,
                        pso_row["PSO"],
                        float(
                            pso_row["PSO Attainment (%)"]
                        ),
                    )
                )

        # Use DELETE + INSERT because the current Simple Edition
        # po_attainment table may not have a UNIQUE(course_id, po_no)
        # constraint.
        execute_query(
            """
            DELETE FROM po_attainment
            WHERE course_id=?
            """,
            (course_id,)
        )

        for _, row in final_df.iterrows():

            execute_query(
                """
                INSERT INTO po_attainment
                (
                    course_id,
                    po_no,
                    direct,
                    indirect,
                    final
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    course_id,
                    row["PO"],
                    float(
                        row["Direct (%)"]
                    ),
                    float(
                        row["Indirect (%)"]
                    ),
                    float(
                        row[
                            "Final PO Attainment (%)"
                        ]
                    )
                )
            )

        st.success(
            "✅ PO Attainment saved successfully."
        )

    except Exception as e:

        st.error(
            "Unable to save PO Attainment."
        )
        st.exception(e)


# --------------------------------------------------------
# Download
# --------------------------------------------------------

st.divider()

st.download_button(
    "📄 Download PO Attainment CSV",
    data=final_df.to_csv(
        index=False
    ).encode("utf-8"),
    file_name=(
        f"{course['course_code']}_PO_Attainment.csv"
    ),
    mime="text/csv",
    use_container_width=True
)
