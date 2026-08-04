import sqlite3


DB_NAME = "database/obe.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():

    conn = get_connection()
    cur = conn.cursor()

    # ----------------------------
    # Course Table
    # ----------------------------
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

    # ----------------------------
    # CO Table
    # ----------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS co(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            co_no TEXT,
            co_statement TEXT
        )
    """)

    # ----------------------------
    # PO Table
    # ----------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS po(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_no TEXT UNIQUE,
            po_statement TEXT
        )
    """)

    # ----------------------------
    # CO PO Mapping
    # ----------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mapping(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            co_no TEXT,
            po_no TEXT,
            level INTEGER
        )
    """)

    conn.commit()

    preload_pos(conn)

    conn.close()


def preload_pos(conn):

    cur = conn.cursor()

    pos = [
        ("PO1","Engineering knowledge"),
        ("PO2","Problem analysis"),
        ("PO3","Design/development of solutions"),
        ("PO4","Conduct investigations"),
        ("PO5","Modern tool usage"),
        ("PO6","Engineer and society"),
        ("PO7","Environment and sustainability"),
        ("PO8","Ethics"),
        ("PO9","Individual and teamwork"),
        ("PO10","Communication"),
        ("PO11","Project management and finance"),
        ("PO12","Life-long learning")
    ]

    for po in pos:

        cur.execute("""
            INSERT OR IGNORE INTO po
            (po_no,po_statement)
            VALUES(?,?)
        """, po)

    conn.commit()