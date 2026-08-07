"""
Course Outcomes Database Functions
OBE Analytics Pro v1.2 RC2
"""

from database.connection import get_connection


# ---------------------------------------------------------
# Save Course Outcomes
# ---------------------------------------------------------
def save_all_cos(course_code, data):
    """
    Save all Course Outcomes for a course.

    Parameters
    ----------
    course_code : str

    data :
        [
            ("CO1", "Understand antenna fundamentals", "L2"),
            ("CO2", "Analyze radiation characteristics", "L4"),
            ...
        ]
    """

    conn = get_connection()
    cur = conn.cursor()

    # Remove existing COs for this course
    cur.execute(
        """
        DELETE FROM co
        WHERE course_code = ?
        """,
        (course_code,),
    )

    # Insert new COs
    rows = [
        (
            course_code,
            co_no,
            co_statement,
            bloom_level,
        )
        for co_no, co_statement, bloom_level in data
    ]

    cur.executemany(
        """
        INSERT INTO co
        (
            course_code,
            co_no,
            co_statement,
            bloom_level
        )
        VALUES (?, ?, ?, ?)
        """,
        rows,
    )

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# Get Course Outcomes
# ---------------------------------------------------------
def get_all_cos(course_code):
    """
    Returns all Course Outcomes for a course.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            co_no,
            co_statement,
            bloom_level
        FROM co
        WHERE course_code = ?
        ORDER BY co_no
        """,
        (course_code,),
    )

    rows = cur.fetchall()

    conn.close()

    return rows


# ---------------------------------------------------------
# Delete Course Outcomes
# ---------------------------------------------------------
def delete_all_cos(course_code):
    """
    Delete all Course Outcomes for a course.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM co
        WHERE course_code = ?
        """,
        (course_code,),
    )

    conn.commit()
    conn.close()