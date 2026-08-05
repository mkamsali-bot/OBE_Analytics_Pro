"""
Student Marks Database Module
OBE Analytics Pro v1.1.2
"""

from database.connection import get_connection


# ---------------------------------------------------------
# Add Student Marks
# ---------------------------------------------------------
def add_student_marks(course_code, reg_no, student_name, le, s1, s2):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO student_marks
        (
            course_code,
            reg_no,
            student_name,
            le,
            s1,
            s2
        )
        VALUES (?,?,?,?,?,?)
    """, (
        course_code,
        reg_no,
        student_name,
        le,
        s1,
        s2
    ))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# Update Student Marks
# ---------------------------------------------------------
def update_student_marks(course_code, reg_no, le, s1, s2):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE student_marks
        SET
            le = ?,
            s1 = ?,
            s2 = ?
        WHERE
            course_code = ?
        AND
            reg_no = ?
    """, (
        le,
        s1,
        s2,
        course_code,
        reg_no
    ))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# Delete Student
# ---------------------------------------------------------
def delete_student_marks(course_code, reg_no):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM student_marks
        WHERE
            course_code = ?
        AND
            reg_no = ?
    """, (
        course_code,
        reg_no
    ))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# Get One Student
# ---------------------------------------------------------
def get_student_marks(course_code, reg_no):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            reg_no,
            student_name,
            le,
            s1,
            s2
        FROM student_marks
        WHERE
            course_code = ?
        AND
            reg_no = ?
    """, (
        course_code,
        reg_no
    ))

    row = cur.fetchone()

    conn.close()

    return row


# ---------------------------------------------------------
# Get Students by Course
# ---------------------------------------------------------
def get_students_by_course(course_code):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            reg_no,
            student_name,
            le,
            s1,
            s2
        FROM student_marks
        WHERE
            course_code = ?
        ORDER BY reg_no
    """, (course_code,))

    rows = cur.fetchall()

    conn.close()

    return rows


# ---------------------------------------------------------
# Save Bulk Marks
# ---------------------------------------------------------
def save_bulk_marks(course_code, students):
    """
    students format

    [
        {
            "reg_no":"221001",
            "student_name":"Rahul",
            "le":20,
            "s1":25,
            "s2":40
        },
        ...
    ]
    """

    conn = get_connection()
    cur = conn.cursor()

    for student in students:

        cur.execute("""
            INSERT INTO student_marks
            (
                course_code,
                reg_no,
                student_name,
                le,
                s1,
                s2
            )
            VALUES (?,?,?,?,?,?)
            ON CONFLICT(course_code, reg_no)
            DO UPDATE SET

                student_name = excluded.student_name,
                le = excluded.le,
                s1 = excluded.s1,
                s2 = excluded.s2
        """, (
            course_code,
            student["reg_no"],
            student["student_name"],
            student["le"],
            student["s1"],
            student["s2"]
        ))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# Delete All Students of a Course
# ---------------------------------------------------------
def clear_course_marks(course_code):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM student_marks
        WHERE course_code = ?
    """, (course_code,))

    conn.commit()
    conn.close()