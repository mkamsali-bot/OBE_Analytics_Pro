"""
Course Database Functions
OBE Analytics Pro v1.1.2
"""

from database.connection import get_connection


# ---------------------------------------------------------
# Add Course
# ---------------------------------------------------------
def save_course(data):
    """
    data =
    (
        course_code,
        course_name,
        faculty,
        department,
        programme,
        semester,
        credits,
        academic_year
    )
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO course(
            course_code,
            course_name,
            faculty,
            department,
            programme,
            semester,
            credits,
            academic_year
        )
        VALUES (?,?,?,?,?,?,?,?)
        ON CONFLICT(course_code)
        DO UPDATE SET

            course_name = excluded.course_name,
            faculty = excluded.faculty,
            department = excluded.department,
            programme = excluded.programme,
            semester = excluded.semester,
            credits = excluded.credits,
            academic_year = excluded.academic_year
    """, data)

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# Get Course
# ---------------------------------------------------------
def get_course(course_code=None):

    conn = get_connection()
    cur = conn.cursor()

    if course_code is None:

        cur.execute("""
            SELECT
                course_code,
                course_name,
                faculty,
                department,
                programme,
                semester,
                credits,
                academic_year
            FROM course
            ORDER BY course_code
            LIMIT 1
        """)

    else:

        cur.execute("""
            SELECT
                course_code,
                course_name,
                faculty,
                department,
                programme,
                semester,
                credits,
                academic_year
            FROM course
            WHERE course_code=?
        """, (course_code,))

    row = cur.fetchone()

    conn.close()

    return row


# ---------------------------------------------------------
# Get All Courses
# ---------------------------------------------------------
def get_all_courses():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        course_code,
        course_name,
        programme,
        semester,
        academic_year
    FROM course
    ORDER BY course_code
""")

    rows = cur.fetchall()

    conn.close()

    return rows


# ---------------------------------------------------------
# Update Course
# ---------------------------------------------------------
def update_course(data):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE course
        SET
            course_name=?,
            faculty=?,
            department=?,
            programme=?,
            semester=?,
            credits=?,
            academic_year=?
        WHERE
            course_code=?
    """, (
        data[1],
        data[2],
        data[3],
        data[4],
        data[5],
        data[6],
        data[7],
        data[0]
    ))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# Delete Course
# ---------------------------------------------------------
def delete_course(course_code):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM course
        WHERE course_code=?
    """, (course_code,))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# Course Exists
# ---------------------------------------------------------
def course_exists(course_code):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM course
        WHERE course_code=?
    """, (course_code,))

    count = cur.fetchone()[0]

    conn.close()

    return count > 0