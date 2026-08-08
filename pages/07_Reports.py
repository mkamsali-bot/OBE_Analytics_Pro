"""
=========================================================
OBE Analytics - Simple Edition
07_Reports.py
OBE Report Export
=========================================================

Provides:
    1. CO Attainment report
    2. CO-PO Mapping report
    3. PO Attainment report
    4. Consolidated Excel export
    5. Consolidated PDF export

The report reads the values already saved/calculated by the
working Simple Edition modules. It does not change attainment
calculations.

PO target:
    Default = 60%

PO status:
    Final PO Attainment >= Target -> Attained
    Otherwise -> Not Attained
=========================================================
"""

import streamlit as st
import pandas as pd

from io import BytesIO

from database import (
    get_active_course,
    fetch_all,
    fetch_dataframe
)


# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="OBE Reports",
    page_icon="📊",
    layout="wide"
)

st.title("📊 OBE Reports & Export")
st.caption(
    "Consolidated CO Attainment, CO–PO Mapping and PO Attainment"
)

st.divider()


# =========================================================
# ACTIVE COURSE
# =========================================================

course = get_active_course()

if course is None:
    st.warning(
        "Please select an Active Course from Course Management."
    )
    st.stop()

course_id = course["id"]

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


# =========================================================
# LOAD CO ATTAINMENT
# =========================================================

co_df = fetch_dataframe(
    """
    SELECT
        co_no,
        attainment
    FROM co_attainment
    WHERE course_id=?
    ORDER BY CAST(
        REPLACE(UPPER(co_no), 'CO', '')
        AS INTEGER
    )
    """,
    (course_id,)
)

if not co_df.empty:

    co_df["CO"] = (
        co_df["co_no"]
        .astype(str)
        .str.strip()
        .str.upper()
        .apply(
            lambda x:
            x if x.startswith("CO")
            else f"CO{x}"
        )
    )

    co_df["CO Attainment (%)"] = pd.to_numeric(
        co_df["attainment"],
        errors="coerce"
    ).fillna(0).round(2)

    co_report = co_df[
        [
            "CO",
            "CO Attainment (%)"
        ]
    ].copy()

else:

    co_report = pd.DataFrame(
        columns=[
            "CO",
            "CO Attainment (%)"
        ]
    )


# =========================================================
# LOAD CO-PO MAPPING
# =========================================================

mapping_df = fetch_dataframe(
    """
    SELECT
        co_no,
        po_no,
        mapping_level
    FROM mapping
    WHERE course_id=?
    ORDER BY
        CAST(
            REPLACE(UPPER(co_no), 'CO', '')
            AS INTEGER
        ),
        CAST(
            REPLACE(UPPER(po_no), 'PO', '')
            AS INTEGER
        )
    """,
    (course_id,)
)

if not mapping_df.empty:

    mapping_df["co_no"] = (
        mapping_df["co_no"]
        .astype(str)
        .str.strip()
        .str.upper()
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
    ).fillna(0).astype(int)

else:

    mapping_df = pd.DataFrame(
        columns=[
            "co_no",
            "po_no",
            "mapping_level"
        ]
    )


# =========================================================
# LOAD CO-PSO MAPPING
# =========================================================

pso_mapping_df = fetch_dataframe(
    """
    SELECT
        co_no,
        pso_no,
        mapping_level
    FROM pso_mapping
    WHERE course_id=?
    ORDER BY
        CAST(REPLACE(UPPER(co_no), 'CO', '') AS INTEGER),
        CAST(REPLACE(UPPER(pso_no), 'PSO', '') AS INTEGER)
    """,
    (course_id,)
)

if not pso_mapping_df.empty:
    pso_mapping_df["co_no"] = (
        pso_mapping_df["co_no"].astype(str).str.strip().str.upper()
    )
    pso_mapping_df["pso_no"] = (
        pso_mapping_df["pso_no"].astype(str).str.strip().str.upper()
    )
    pso_mapping_df["mapping_level"] = pd.to_numeric(
        pso_mapping_df["mapping_level"],
        errors="coerce"
    ).fillna(0).astype(int)
else:
    pso_mapping_df = pd.DataFrame(
        columns=["co_no", "pso_no", "mapping_level"]
    )


# =========================================================
# LOAD PSO ATTAINMENT
# =========================================================

pso_df = fetch_dataframe(
    """
    SELECT
        pso_no,
        attainment
    FROM pso_attainment
    WHERE course_id=?
    ORDER BY
        CAST(REPLACE(UPPER(pso_no), 'PSO', '') AS INTEGER)
    """,
    (course_id,)
)

if not pso_df.empty:
    pso_df["PSO"] = (
        pso_df["pso_no"].astype(str).str.strip().str.upper().apply(
            lambda x: x if x.startswith("PSO") else f"PSO{x}"
        )
    )
    pso_report = pd.DataFrame({
        "PSO": pso_df["PSO"],
        "PSO Attainment (%)": pd.to_numeric(
            pso_df["attainment"], errors="coerce"
        ).fillna(0).round(2),
    })
else:
    pso_report = pd.DataFrame(
        columns=["PSO", "PSO Attainment (%)"]
    )


# =========================================================
# LOAD PO ATTAINMENT
# =========================================================

po_df = fetch_dataframe(
    """
    SELECT
        po_no,
        direct,
        indirect,
        final
    FROM po_attainment
    WHERE course_id=?
    ORDER BY
        CAST(
            REPLACE(UPPER(po_no), 'PO', '')
            AS INTEGER
        )
    """,
    (course_id,)
)

# ---------------------------------------------------------
# Target
# ---------------------------------------------------------

po_target = st.number_input(
    "PO Attainment Target (%)",
    min_value=0.0,
    max_value=100.0,
    value=60.0,
    step=1.0,
    key="report_po_target"
)


if not po_df.empty:

    po_df["PO"] = (
        po_df["po_no"]
        .astype(str)
        .str.strip()
        .str.upper()
        .apply(
            lambda x:
            x if x.startswith("PO")
            else f"PO{x}"
        )
    )

    po_report = pd.DataFrame(
        {
            "PO": po_df["PO"],
            "Direct (%)": pd.to_numeric(
                po_df["direct"],
                errors="coerce"
            ).fillna(0).round(2),
            "Indirect (%)": pd.to_numeric(
                po_df["indirect"],
                errors="coerce"
            ).fillna(0).round(2),
            "Final (%)": pd.to_numeric(
                po_df["final"],
                errors="coerce"
            ).fillna(0).round(2)
        }
    )

    po_report["Target (%)"] = po_target

    po_report["Status"] = po_report[
        "Final (%)"
    ].apply(
        lambda x:
        "Attained"
        if x >= po_target
        else "Not Attained"
    )

else:

    po_report = pd.DataFrame(
        columns=[
            "PO",
            "Direct (%)",
            "Indirect (%)",
            "Final (%)",
            "Target (%)",
            "Status"
        ]
    )


# =========================================================
# CO-PO MATRIX
# =========================================================

if not mapping_df.empty:

    matrix_df = mapping_df.pivot_table(
        index="co_no",
        columns="po_no",
        values="mapping_level",
        aggfunc="max",
        fill_value=0
    )

    matrix_df.index = matrix_df.index.map(
        lambda x:
        x if str(x).startswith("CO")
        else f"CO{x}"
    )

    matrix_df.columns = matrix_df.columns.map(
        lambda x:
        x if str(x).startswith("PO")
        else f"PO{x}"
    )

    matrix_df = matrix_df.reset_index()

    matrix_df = matrix_df.rename(
        columns={
            "co_no": "CO"
        }
    )

else:

    matrix_df = pd.DataFrame(
        columns=["CO"]
    )


# =========================================================
# CO-PSO MATRIX
# =========================================================

if not pso_mapping_df.empty:
    pso_matrix_df = pso_mapping_df.pivot_table(
        index="co_no",
        columns="pso_no",
        values="mapping_level",
        aggfunc="max",
        fill_value=0
    )

    pso_matrix_df.index = pso_matrix_df.index.map(
        lambda x: x if str(x).startswith("CO") else f"CO{x}"
    )

    pso_matrix_df.columns = pso_matrix_df.columns.map(
        lambda x: x if str(x).startswith("PSO") else f"PSO{x}"
    )

    pso_matrix_df = pso_matrix_df.reset_index()
    pso_matrix_df = pso_matrix_df.rename(columns={"co_no": "CO"})
else:
    pso_matrix_df = pd.DataFrame(columns=["CO"])


# =========================================================
# REPORT SELECTOR
# =========================================================

st.divider()

st.subheader("Select Report")

report_choice = st.radio(
    "Report",
    [
        "CO Attainment",
        "PO Attainment",
        "CO–PO Mapping",
        "CO–PSO Mapping",
        "PSO Attainment",
        "Consolidated OBE Report"
    ],
    horizontal=True,
    key="report_choice"
)


# =========================================================
# DISPLAY REPORT
# =========================================================

if report_choice == "CO Attainment":

    st.subheader("🎯 CO Attainment")

    if co_report.empty:

        st.warning(
            "No CO Attainment data is available."
        )

    else:

        st.dataframe(
            co_report,
            use_container_width=True,
            hide_index=True
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Number of COs",
                len(co_report)
            )

        with c2:
            st.metric(
                "Average CO Attainment",
                f"{co_report['CO Attainment (%)'].mean():.2f}%"
            )

        with c3:
            st.metric(
                "Highest CO Attainment",
                f"{co_report['CO Attainment (%)'].max():.2f}%"
            )


elif report_choice == "PO Attainment":

    st.subheader("🎯 PO Attainment")

    if po_report.empty:

        st.warning(
            "No PO Attainment data is available."
        )

    else:

        st.dataframe(
            po_report,
            use_container_width=True,
            hide_index=True
        )

        attained_count = int(
            (
                po_report["Status"]
                == "Attained"
            ).sum()
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Total POs",
                len(po_report)
            )

        with c2:
            st.metric(
                "POs Attained",
                attained_count
            )

        with c3:
            st.metric(
                "Average Final PO",
                f"{po_report['Final (%)'].mean():.2f}%"
            )


elif report_choice == "CO–PO Mapping":

    st.subheader("🔗 CO–PO Mapping Matrix")

    if matrix_df.empty:

        st.warning(
            "No CO–PO Mapping data is available."
        )

    else:

        st.dataframe(
            matrix_df,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "Mapping levels: 0 = No Mapping, "
            "1 = Low, 2 = Moderate, 3 = High."
        )


elif report_choice == "CO–PSO Mapping":

    st.subheader("🔗 CO–PSO Mapping Matrix")

    if pso_matrix_df.empty:
        st.warning("No CO–PSO Mapping data is available.")
    else:
        st.dataframe(
            pso_matrix_df,
            use_container_width=True,
            hide_index=True
        )
        st.caption(
            "Mapping levels: 0 = No Mapping, "
            "1 = Low, 2 = Moderate, 3 = High."
        )


elif report_choice == "PSO Attainment":

    st.subheader("🎯 PSO Attainment")

    if pso_report.empty:
        st.warning("No PSO Attainment data is available.")
    else:
        st.dataframe(
            pso_report,
            use_container_width=True,
            hide_index=True
        )


else:

    st.subheader("📊 Consolidated OBE Report")

    st.markdown(
        f"""
### Course Information

| Field | Value |
|---|---|
| Course Code | {course["course_code"]} |
| Course Name | {course["course_name"]} |
| Faculty | {course["faculty"]} |
| Semester | {course["semester"]} |
| Academic Year | {course["academic_year"]} |
| PO Target | {po_target:.2f}% |
"""
    )

    st.subheader("CO Attainment")

    if co_report.empty:
        st.info(
            "No CO Attainment data available."
        )
    else:
        st.dataframe(
            co_report,
            use_container_width=True,
            hide_index=True
        )

    st.subheader("CO–PO Mapping")

    if matrix_df.empty:
        st.info(
            "No CO–PO Mapping data available."
        )
    else:
        st.dataframe(
            matrix_df,
            use_container_width=True,
            hide_index=True
        )

    st.subheader("CO–PSO Mapping")

    if pso_matrix_df.empty:
        st.info("No CO–PSO Mapping data available.")
    else:
        st.dataframe(
            pso_matrix_df,
            use_container_width=True,
            hide_index=True
        )

    st.subheader("PSO Attainment")

    if pso_report.empty:
        st.info("No PSO Attainment data available.")
    else:
        st.dataframe(
            pso_report,
            use_container_width=True,
            hide_index=True
        )

    st.subheader("PO Attainment")

    if po_report.empty:
        st.info(
            "No PO Attainment data available."
        )
    else:
        st.dataframe(
            po_report,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# EXCEL EXPORT
# =========================================================

st.divider()

st.subheader("📗 Excel Export")

st.caption(
    "The Excel workbook contains separate sheets for "
    "Course Summary, CO Attainment, CO–PO Mapping and "
    "PO Attainment."
)


def create_excel_report():

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        summary_df = pd.DataFrame(
            [
                [
                    "Course Code",
                    course["course_code"]
                ],
                [
                    "Course Name",
                    course["course_name"]
                ],
                [
                    "Faculty",
                    course["faculty"]
                ],
                [
                    "Semester",
                    course["semester"]
                ],
                [
                    "Academic Year",
                    course["academic_year"]
                ],
                [
                    "PO Target (%)",
                    po_target
                ]
            ],
            columns=[
                "Field",
                "Value"
            ]
        )

        summary_df.to_excel(
            writer,
            sheet_name="Course Summary",
            index=False
        )

        co_report.to_excel(
            writer,
            sheet_name="CO Attainment",
            index=False
        )

        matrix_df.to_excel(
            writer,
            sheet_name="CO-PO Mapping",
            index=False
        )

        po_report.to_excel(
            writer,
            sheet_name="PO Attainment",
            index=False
        )

        pso_matrix_df.to_excel(
            writer,
            sheet_name="CO-PSO Mapping",
            index=False
        )

        pso_report.to_excel(
            writer,
            sheet_name="PSO Attainment",
            index=False
        )

        workbook = writer.book

        for worksheet in workbook.worksheets:

            worksheet.freeze_panes = "A2"

            for column_cells in worksheet.columns:

                max_length = 0

                column_letter = (
                    column_cells[0]
                    .column_letter
                )

                for cell in column_cells:

                    value = (
                        ""
                        if cell.value is None
                        else str(cell.value)
                    )

                    max_length = max(
                        max_length,
                        len(value)
                    )

                worksheet.column_dimensions[
                    column_letter
                ].width = min(
                    max_length + 3,
                    40
                )

    output.seek(0)

    return output.getvalue()


excel_bytes = create_excel_report()

st.download_button(
    "⬇️ Download OBE Report — Excel",
    data=excel_bytes,
    file_name=(
        f"{course['course_code']}_OBE_Report.xlsx"
    ),
    mime=(
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    ),
    use_container_width=True
)


# =========================================================
# PDF EXPORT
# =========================================================

st.subheader("📕 PDF Export")

st.caption(
    "Creates a consolidated PDF report containing the "
    "course summary, CO attainment, CO–PO mapping and "
    "PO attainment."
)


def create_pdf_report():

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import (
        getSampleStyleSheet,
        ParagraphStyle
    )
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        PageBreak
    )

    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        leading=22
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=9,
        leading=11
    )

    story = []

    story.append(
        Paragraph(
            "OBE ANALYTICS REPORT",
            title_style
        )
    )

    story.append(
        Spacer(1, 6 * mm)
    )

    story.append(
        Paragraph(
            str(course["course_name"]),
            heading_style
        )
    )

    summary_data = [
        ["Field", "Value"],
        [
            "Course Code",
            str(course["course_code"])
        ],
        [
            "Faculty",
            str(course["faculty"])
        ],
        [
            "Semester",
            str(course["semester"])
        ],
        [
            "Academic Year",
            str(course["academic_year"])
        ],
        [
            "PO Target",
            f"{po_target:.2f}%"
        ]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            45 * mm,
            100 * mm
        ]
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                )
            ]
        )
    )

    story.append(summary_table)

    story.append(
        Spacer(1, 8 * mm)
    )

    # CO Attainment
    story.append(
        Paragraph(
            "1. CO Attainment",
            heading_style
        )
    )

    co_data = [
        [
            "CO",
            "Attainment (%)"
        ]
    ]

    for _, row in co_report.iterrows():

        co_data.append(
            [
                str(row["CO"]),
                f"{float(row['CO Attainment (%)']):.2f}"
            ]
        )

    if len(co_data) == 1:
        co_data.append(
            [
                "No data",
                "-"
            ]
        )

    co_table = Table(
        co_data,
        colWidths=[
            45 * mm,
            55 * mm
        ]
    )

    co_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                )
            ]
        )
    )

    story.append(co_table)

    story.append(
        Spacer(1, 8 * mm)
    )

    # Mapping
    story.append(
        Paragraph(
            "2. CO–PO Mapping",
            heading_style
        )
    )

    if not matrix_df.empty:

        mapping_headers = list(
            matrix_df.columns
        )

        mapping_data = [
            mapping_headers
        ]

        for row in matrix_df.itertuples(
            index=False,
            name=None
        ):

            mapping_data.append(
                [
                    str(value)
                    for value in row
                ]
            )

        mapping_table = Table(
            mapping_data,
            colWidths=[
                16 * mm
            ] + [
                12.8 * mm
            ] * (len(mapping_headers) - 1),
            repeatRows=1
        )

        mapping_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.grey
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold"
                    ),
                    (
                        "ALIGN",
                        (1, 1),
                        (-1, -1),
                        "CENTER"
                    )
                ]
            )
        )

        story.append(mapping_table)

    else:

        story.append(
            Paragraph(
                "No CO–PO mapping data available.",
                body_style
            )
        )

    story.append(
        PageBreak()
    )

    # CO-PSO Mapping
    story.append(
        Paragraph(
            "3. CO–PSO Mapping",
            heading_style
        )
    )

    if not pso_matrix_df.empty:

        pso_mapping_headers = list(pso_matrix_df.columns)

        pso_mapping_data = [pso_mapping_headers]

        for row in pso_matrix_df.itertuples(
            index=False,
            name=None
        ):
            pso_mapping_data.append(
                [str(value) for value in row]
            )

        pso_mapping_table = Table(
            pso_mapping_data,
            colWidths=[
                22 * mm
            ] + [
                35 * mm
            ] * (len(pso_mapping_headers) - 1),
            repeatRows=1
        )

        pso_mapping_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.grey
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold"
                    ),
                    (
                        "ALIGN",
                        (1, 1),
                        (-1, -1),
                        "CENTER"
                    )
                ]
            )
        )

        story.append(pso_mapping_table)

    else:

        story.append(
            Paragraph(
                "No CO–PSO mapping data available.",
                body_style
            )
        )

    story.append(Spacer(1, 8 * mm))

    # PSO Attainment
    story.append(
        Paragraph(
            "4. PSO Attainment",
            heading_style
        )
    )

    pso_data = [["PSO", "Attainment (%)"]]

    for _, row in pso_report.iterrows():
        pso_data.append(
            [
                str(row["PSO"]),
                f"{float(row['PSO Attainment (%)']):.2f}"
            ]
        )

    if len(pso_data) == 1:
        pso_data.append(["No data", "-"])

    pso_table = Table(
        pso_data,
        colWidths=[45 * mm, 55 * mm],
        repeatRows=1
    )

    pso_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                )
            ]
        )
    )

    story.append(pso_table)

    story.append(Spacer(1, 8 * mm))

    # PO Attainment
    story.append(
        Paragraph(
            "5. PO Attainment",
            heading_style
        )
    )

    po_data = [
        [
            "PO",
            "Direct (%)",
            "Indirect (%)",
            "Final (%)",
            "Target (%)",
            "Status"
        ]
    ]

    for _, row in po_report.iterrows():

        po_data.append(
            [
                str(row["PO"]),
                f"{float(row['Direct (%)']):.2f}",
                f"{float(row['Indirect (%)']):.2f}",
                f"{float(row['Final (%)']):.2f}",
                f"{float(row['Target (%)']):.2f}",
                str(row["Status"])
            ]
        )

    if len(po_data) == 1:
        po_data.append(
            [
                "No data",
                "-",
                "-",
                "-",
                "-",
                "-"
            ]
        )

    po_table = Table(
        po_data,
        repeatRows=1
    )

    po_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "ALIGN",
                    (1, 1),
                    (-2, -1),
                    "RIGHT"
                )
            ]
        )
    )

    story.append(po_table)

    story.append(
        Spacer(1, 8 * mm)
    )

    if not po_report.empty:

        attained = int(
            (
                po_report["Status"]
                == "Attained"
            ).sum()
        )

        total = len(po_report)

        story.append(
            Paragraph(
                f"POs Attained: {attained} / {total}",
                body_style
            )
        )

        story.append(
            Paragraph(
                "Direct and indirect attainment weights are "
                f"based on the active course settings "
                f"({float(course['direct_weight']):.0f}% Direct + "
                f"{float(course['indirect_weight']):.0f}% Indirect "
                "when indirect attainment is enabled).",
                body_style
            )
        )

    document.build(story)

    output.seek(0)

    return output.getvalue()


try:

    pdf_bytes = create_pdf_report()

    st.download_button(
        "⬇️ Download OBE Report — PDF",
        data=pdf_bytes,
        file_name=(
            f"{course['course_code']}_OBE_Report.pdf"
        ),
        mime="application/pdf",
        use_container_width=True
    )

except Exception as e:

    st.error(
        "PDF export could not be generated."
    )

    st.exception(e)


# =========================================================
# REPORT STATUS
# =========================================================

st.divider()

st.subheader("✅ Report Data Status")

status_items = {
    "CO Attainment": not co_report.empty,
    "CO–PO Mapping": not matrix_df.empty,
    "CO–PSO Mapping": not pso_matrix_df.empty,
    "PO Attainment": not po_report.empty,
    "PSO Attainment": not pso_report.empty
}

for name, available in status_items.items():

    if available:
        st.success(
            f"✅ {name} available"
        )
    else:
        st.warning(
            f"⚠️ {name} not available"
        )
