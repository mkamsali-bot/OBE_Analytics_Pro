"""
Reports Module
OBE Analytics Pro v1.0.0
"""

import io
import pandas as pd
import streamlit as st

from database import (
    get_course,
    get_all_cos,
    get_all_pos,
    get_mapping,
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


# ==========================================================
# EXCEL EXPORT
# ==========================================================

def export_excel():

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        # ---------------- Course ----------------

        course = get_course()

        if course:
            pd.DataFrame([dict(course)]).to_excel(
                writer,
                sheet_name="Course",
                index=False
            )

        # ---------------- CO ----------------

        cos = get_all_cos()

        if cos:
            pd.DataFrame(
                [dict(r) for r in cos]
            ).to_excel(
                writer,
                sheet_name="Course Outcomes",
                index=False
            )

        # ---------------- PO ----------------

        pos = get_all_pos()

        if pos:
            pd.DataFrame(
                [dict(r) for r in pos]
            ).to_excel(
                writer,
                sheet_name="Program Outcomes",
                index=False
            )

        # ---------------- Mapping ----------------

        mapping = get_mapping()

        if mapping:
            pd.DataFrame(
                [dict(r) for r in mapping]
            ).to_excel(
                writer,
                sheet_name="CO-PO Mapping",
                index=False
            )

    output.seek(0)

    return output


# ==========================================================
# PDF EXPORT
# ==========================================================

def export_pdf():

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4)
    )

    styles = getSampleStyleSheet()

    elements = []

    # ======================================================
    # Title
    # ======================================================

    elements.append(
        Paragraph(
            "OBE ANALYTICS PRO",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            "Course Outcome Report",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 20))

    # ======================================================
    # Course Information
    # ======================================================

    course = get_course()

    if course:

        elements.append(
            Paragraph(
                "<b>Course Information</b>",
                styles["Heading2"]
            )
        )

        course_table = [

            ["Course Code", course["course_code"]],
            ["Course Name", course["course_name"]],
            ["Faculty", course["faculty"]],
            ["Department", course["department"]],
            ["Programme", course["programme"]],
            ["Semester", str(course["semester"])],
            ["Credits", str(course["credits"])],
            ["Academic Year", course["academic_year"]],

        ]

        table = Table(
            course_table,
            colWidths=[2 * inch, 5 * inch]
        )

        table.setStyle(TableStyle([

            ("GRID", (0, 0), (-1, -1), 1, colors.black),

            ("BACKGROUND", (0, 0), (-1, -1), colors.beige),

            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),

        ]))

        elements.append(table)

        elements.append(Spacer(1, 20))

    # ======================================================
    # Course Outcomes
    # ======================================================

    elements.append(
        Paragraph(
            "<b>Course Outcomes</b>",
            styles["Heading2"]
        )
    )

    co_table = [["CO", "Course Outcome", "Bloom"]]

    for row in get_all_cos():

        co_table.append([
            row["co_no"],
            row["co_statement"],
            row["bloom_level"]
        ])

    table = Table(co_table)

    table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),

        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), 1, colors.black),

        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),

    ]))

    elements.append(table)

    elements.append(Spacer(1, 20))

    # ======================================================
    # Program Outcomes
    # ======================================================

    elements.append(
        Paragraph(
            "<b>Program Outcomes</b>",
            styles["Heading2"]
        )
    )

    po_table = [["PO", "Program Outcome"]]

    for row in get_all_pos():

        po_table.append([
            row["po_no"],
            row["po_statement"]
        ])

    table = Table(po_table)

    table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),

        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), 1, colors.black),

        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),

    ]))

    elements.append(table)

    elements.append(Spacer(1, 20))

    # ======================================================
    # CO–PO Mapping Matrix
    # ======================================================

    elements.append(
        Paragraph(
            "<b>CO–PO Mapping Matrix</b>",
            styles["Heading2"]
        )
    )

    cos = get_all_cos()
    pos = get_all_pos()
    mappings = get_mapping()

    mapping_lookup = {}

    for item in mappings:
        mapping_lookup[(item["co_no"], item["po_no"])] = item["level"]

    matrix = [["CO"]]

    for po in pos:
        matrix[0].append(po["po_no"])

    for co in cos:

        row = [co["co_no"]]

        for po in pos:

            row.append(
                mapping_lookup.get(
                    (co["co_no"], po["po_no"]),
                    0
                )
            )

        matrix.append(row)

    mapping_table = Table(matrix)

    mapping_table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),

        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("BACKGROUND", (0, 1), (0, -1), colors.lightgrey),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),

        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

    ]))

    elements.append(mapping_table)

    # ======================================================
    # Finish PDF
    # ======================================================

    doc.build(elements)

    buffer.seek(0)

    return buffer


# ==========================================================
# REPORTS PAGE
# ==========================================================

def show_reports():

    st.title("📄 Reports")

    st.write("Generate and download OBE reports.")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            "📊 Download Excel Report",
            data=export_excel(),
            file_name="OBE_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with col2:

        st.download_button(
            "📄 Download PDF Report",
            data=export_pdf(),
            file_name="OBE_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    st.success("✅ Reports are ready for download.")