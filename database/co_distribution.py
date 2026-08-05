"""
CO Distribution Database Module
OBE Analytics Pro v1.1
"""

from database.connection import get_connection


# ---------------------------------------------------------
# Get All Courses
# ---------------------------------------------------------
def get_courses():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT course_code, course_name
        FROM course
        ORDER BY course_code
    """)

    rows = cur.fetchall()
    conn.close()

    return rows


# ---------------------------------------------------------
# Get CO Distribution for a Course
# ---------------------------------------------------------
def get_distribution(course_code):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            assessment_name,
            co_no,
            allocated_marks
        FROM co_distribution
        WHERE course_code = ?
        ORDER BY assessment_name, co_no
    """, (course_code,))

    rows = cur.fetchall()

    conn.close()

    return rows


# ---------------------------------------------------------
# Delete Existing Distribution
# ---------------------------------------------------------
def delete_distribution(course_code):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM co_distribution
        WHERE course_code = ?
    """, (course_code,))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# Save Distribution
# ---------------------------------------------------------
def save_distribution(course_code, distribution):
    """
    distribution format

    [
        ("LE","CO1",5),
        ("LE","CO2",5),
        ("LE","CO3",5),

        ("S1","CO1",15),
        ("S1","CO2",15),

        ("S2","CO3",15),
        ("S2","CO4",15),
        ("S2","CO5",15)
    ]
    """

    conn = get_connection()
    cur = conn.cursor()

    # Remove previous entries
    cur.execute("""
        DELETE FROM co_distribution
        WHERE course_code = ?
    """, (course_code,))

    # Insert latest entries
    cur.executemany("""
        INSERT INTO co_distribution
        (
            course_code,
            assessment_name,
            co_no,
            allocated_marks
        )
        VALUES (?,?,?,?)
    """, [(course_code, a, c, m) for a, c, m in distribution])

    conn.commit()
    conn.close()

    return True


# ---------------------------------------------------------
# Check Distribution Exists
# ---------------------------------------------------------
def distribution_exists(course_code):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM co_distribution
        WHERE course_code = ?
    """, (course_code,))

    count = cur.fetchone()[0]

    conn.close()

    return count > 0