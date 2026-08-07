"""
Database Initialization
OBE Analytics Pro v1.2 RC2
"""

from database.connection import get_connection
from database.po import preload_pos


def initialize_database():
    conn = get_connection()
    cur = conn.cursor()

    # ==========================================================
    # COURSE MASTER
    # ==========================================================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS course (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT UNIQUE,
        course_name TEXT,
        faculty TEXT,
        department TEXT,
        programme TEXT,
        semester INTEGER,
        credits INTEGER,
        academic_year TEXT
    )
    """)

    # ==========================================================
    # COURSE OUTCOMES
    # ==========================================================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS co (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT,
        co_no TEXT,
        co_statement TEXT,
        bloom_level TEXT,
        UNIQUE(course_code, co_no)
    )
    """)

    # ==========================================================
    # PROGRAM OUTCOMES
    # ==========================================================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS po (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        po_no TEXT UNIQUE,
        po_statement TEXT
    )
    """)

    # ==========================================================
    # CO-PO MAPPING
    # ==========================================================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS co_po_mapping (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT,
        co_no TEXT,
        po_no TEXT,
        level INTEGER,
        UNIQUE(course_code, co_no, po_no)
    )
    """)

    # ==========================================================
    # ASSESSMENT PATTERN
    # ==========================================================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS assessment_pattern (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assessment_name TEXT UNIQUE,
        max_marks INTEGER NOT NULL
    )
    """)

        # ==========================================================
    # CO DISTRIBUTION
    # ==========================================================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS co_distribution (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT,
        assessment_name TEXT,
        co_no TEXT,
        allocated_marks REAL,
        UNIQUE(course_code, assessment_name, co_no)
    )
    """)

    # ==========================================================
    # STUDENT MARKS
    # ==========================================================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS student_marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT,
        reg_no TEXT,
        student_name TEXT,
        le REAL DEFAULT 0,
        s1 REAL DEFAULT 0,
        s2 REAL DEFAULT 0,
        UNIQUE(course_code, reg_no)
    )
    """)

    # ==========================================================
    # COURSE END SURVEY
    # ==========================================================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS course_end_survey (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT,
        co_no TEXT,
        survey_attainment REAL,
        UNIQUE(course_code, co_no)
    )
    """)

    # ==========================================================
    # ATTAINMENT SETTINGS
    # ==========================================================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS attainment_settings (
        id INTEGER PRIMARY KEY,
        direct_weight REAL,
        indirect_weight REAL,
        level3 REAL,
        level2 REAL,
        level1 REAL
    )
    """)

    # ==========================================================
    # DIRECT CO ATTAINMENT
    # ==========================================================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS direct_attainment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT,
        co_no TEXT,
        attainment REAL,
        UNIQUE(course_code, co_no)
    )
    """)

    # ==========================================================
    # FINAL CO ATTAINMENT
    # ==========================================================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS final_co_attainment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT,
        co_no TEXT,
        direct REAL,
        survey REAL,
        final REAL,
        UNIQUE(course_code, co_no)
    )
    """)

    # ==========================================================
    # PO ATTAINMENT
    # ==========================================================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS po_attainment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT,
        po_no TEXT,
        attainment REAL,
        UNIQUE(course_code, po_no)
    )
    """)

        # ==========================================================
    # DEFAULT ASSESSMENT PATTERN
    # ==========================================================
    cur.execute("SELECT COUNT(*) FROM assessment_pattern")

    if cur.fetchone()[0] == 0:

        cur.executemany(
            """
            INSERT INTO assessment_pattern
            (assessment_name, max_marks)
            VALUES (?, ?)
            """,
            [
                ("LE", 25),
                ("S1", 30),
                ("S2", 45)
            ]
        )

    # ==========================================================
    # DEFAULT ATTAINMENT SETTINGS
    # ==========================================================
    cur.execute("SELECT COUNT(*) FROM attainment_settings")

    if cur.fetchone()[0] == 0:

        cur.execute("""
        INSERT INTO attainment_settings
        (
            id,
            direct_weight,
            indirect_weight,
            level3,
            level2,
            level1
        )
        VALUES
        (
            1,
            80,
            20,
            70,
            60,
            0
        )
        """)

    conn.commit()
    conn.close()

    # Preload NBA Program Outcomes
    preload_pos()