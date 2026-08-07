"""
CO-PO Mapping Database Functions
OBE Analytics Pro v1.2 RC2
"""

from database.connection import get_connection


def delete_mapping(course_code):
    """
    Delete all mappings for the selected course.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM co_po_mapping
        WHERE course_code = ?
        """,
        (course_code,),
    )

    conn.commit()
    conn.close()


def save_mapping(course_code, data):
    """
    Save CO-PO mapping for one course.

    Parameters
    ----------
    course_code : str

    data :
        [
            ("CO1", "PO1", 3),
            ("CO1", "PO2", 2),
            ("CO2", "PO1", 1),
            ...
        ]
    """

    conn = get_connection()
    cur = conn.cursor()

    # Remove existing mapping for this course
    cur.execute(
        """
        DELETE FROM co_po_mapping
        WHERE course_code = ?
        """,
        (course_code,),
    )

        # Insert fresh mapping

    rows = [
        (course_code, co_no, po_no, level)
        for co_no, po_no, level in data
    ]

    print("Course:", course_code)
    print("Rows:", rows)

    cur.executemany(
        """
        INSERT INTO co_po_mapping
        (
            course_code,
            co_no,
            po_no,
            level
        )
        VALUES (?, ?, ?, ?)
        """,
        rows,
    )

    conn.commit()
    conn.close()


def get_mapping(course_code):
    """
    Returns all mappings for the selected course.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            co_no,
            po_no,
            level
        FROM co_po_mapping
        WHERE course_code = ?
        ORDER BY co_no, po_no
        """,
        (course_code,),
    )

    rows = cur.fetchall()

    conn.close()

    return rows