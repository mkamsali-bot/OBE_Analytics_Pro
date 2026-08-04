import sqlite3

DB_NAME = "database/obe.db"


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================================
# DATABASE INITIALIZATION
# ==========================================================

def initialize_database():

    conn = get_connection()
    cur = conn.cursor()

    # ------------------------------------------------------
    # COURSE TABLE
    # ------------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS course(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT,
            course_name TEXT,
            faculty TEXT,
            department TEXT,
            programme TEXT,
            semester INTEGER,
            credits INTEGER,
            academic_year TEXT
        )
    """)

    # ------------------------------------------------------
    # COURSE OUTCOMES
    # ------------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS co(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            co_no TEXT UNIQUE,
            co_statement TEXT,
            bloom_level TEXT
        )
    """)

    # ------------------------------------------------------
    # PROGRAM OUTCOMES
    # ------------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS po(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_no TEXT UNIQUE,
            po_statement TEXT
        )
    """)

    # ------------------------------------------------------
    # CO–PO MAPPING
    # ------------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS co_po_mapping(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            co_no TEXT,
            po_no TEXT,
            level INTEGER
        )
    """)

    conn.commit()

    preload_pos(conn)

    conn.close()


# ==========================================================
# PRELOAD NBA PROGRAM OUTCOMES
# ==========================================================

def preload_pos(conn):

    cur = conn.cursor()

    pos = [

        ("PO1", "Engineering Knowledge"),

        ("PO2", "Problem Analysis"),

        ("PO3", "Design/Development of Solutions"),

        ("PO4", "Conduct Investigations of Complex Problems"),

        ("PO5", "Modern Tool Usage"),

        ("PO6", "The Engineer and Society"),

        ("PO7", "Environment and Sustainability"),

        ("PO8", "Ethics"),

        ("PO9", "Individual and Team Work"),

        ("PO10", "Communication"),

        ("PO11", "Project Management and Finance"),

        ("PO12", "Life-long Learning")

    ]

    for po in pos:

        cur.execute("""
            INSERT OR IGNORE INTO po
            (po_no, po_statement)
            VALUES (?, ?)
        """, po)

    conn.commit()

# ==========================================================
# COURSE FUNCTIONS
# ==========================================================

def save_course(data):
    """
    Saves the single course.
    Version 1.0 supports one course only.
    """

    conn = get_connection()
    cur = conn.cursor()

    # Remove existing course
    cur.execute("DELETE FROM course")

    # Insert new course
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
    """
    Returns the saved course.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM course
        LIMIT 1
    """)

    row = cur.fetchone()

    conn.close()

    return row


def delete_course():
    """
    Deletes the current course.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM course")

    conn.commit()
    conn.close()

# ==========================================================
# COURSE OUTCOME (CO) FUNCTIONS
# ==========================================================

def get_all_cos():
    """
    Returns all Course Outcomes.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM co
        ORDER BY id
    """)

    rows = cur.fetchall()

    conn.close()

    return rows


def save_all_cos(data):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM co")

    cur.executemany("""
        INSERT INTO co(
            co_no,
            co_statement,
            bloom_level
        )
        VALUES (?, ?, ?)
    """, data)

    conn.commit()
    conn.close()

def delete_all_cos():
    """
    Deletes all Course Outcomes.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM co")

    conn.commit()
    conn.close()


def get_co_count():
    """
    Returns the number of COs.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM co")

    count = cur.fetchone()[0]

    conn.close()

    return count