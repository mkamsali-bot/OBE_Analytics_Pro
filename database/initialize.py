"""
Database Initialization
OBE Analytics Pro v1.0.0
"""

from database.connection import get_connection


def initialize_database():

    conn = get_connection()
    cur = conn.cursor()

    # -------------------------------------------------
    # COURSE
    # -------------------------------------------------

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

    # -------------------------------------------------
    # COURSE OUTCOMES
    # -------------------------------------------------

    cur.execute("""
    CREATE TABLE IF NOT EXISTS co(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        co_no TEXT UNIQUE,
        co_statement TEXT,
        bloom_level TEXT

    )
    """)

    # -------------------------------------------------
    # PROGRAM OUTCOMES
    # -------------------------------------------------

    cur.execute("""
    CREATE TABLE IF NOT EXISTS po(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        po_no TEXT UNIQUE,
        po_statement TEXT

    )
    """)

    # -------------------------------------------------
    # CO-PO MAPPING
    # -------------------------------------------------

    cur.execute("""
    CREATE TABLE IF NOT EXISTS co_po_mapping(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        co_no TEXT,
        po_no TEXT,
        level INTEGER

    )
    """)

    conn.commit()
    conn.close()