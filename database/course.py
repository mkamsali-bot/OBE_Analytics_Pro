"""
Course Database Functions
OBE Analytics Pro v1.0.0
"""

from database.connection import get_connection


def save_course(data):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM course")

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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    conn.close()


def get_course():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM course LIMIT 1")

    row = cur.fetchone()

    conn.close()

    return row


def course_exists():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM course")

    count = cur.fetchone()[0]

    conn.close()

    return count > 0