import sqlite3
import os

# ---------------------------------------------------
# Database Configuration
# ---------------------------------------------------

DB_FOLDER = "database"
DB_NAME = os.path.join(DB_FOLDER, "obe.db")

os.makedirs(DB_FOLDER, exist_ok=True)


# ---------------------------------------------------
# Connection
# ---------------------------------------------------

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------
# Initialize Database
# ---------------------------------------------------

def initialize_database():

    conn = get_connection()
    cur = conn.cursor()

    # ---------------- Course ----------------

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

    # ---------------- CO ----------------

    cur.execute("""
    CREATE TABLE IF NOT EXISTS co(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        co_no TEXT UNIQUE,
        co_statement TEXT,
        bloom_level TEXT
    )
    """)

    # ---------------- PO ----------------

    cur.execute("""
    CREATE TABLE IF NOT EXISTS po(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        po_no TEXT UNIQUE,
        po_statement TEXT
    )
    """)

    # ---------------- CO-PO Mapping ----------------

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


# ---------------------------------------------------
# Preload NBA POs
# ---------------------------------------------------

def preload_pos(conn):

    cur = conn.cursor()

    pos = [

        ("PO1","Engineering Knowledge"),
        ("PO2","Problem Analysis"),
        ("PO3","Design/Development of Solutions"),
        ("PO4","Conduct Investigations"),
        ("PO5","Modern Tool Usage"),
        ("PO6","Engineer and Society"),
        ("PO7","Environment and Sustainability"),
        ("PO8","Ethics"),
        ("PO9","Individual and Team Work"),
        ("PO10","Communication"),
        ("PO11","Project Management and Finance"),
        ("PO12","Life-long Learning")

    ]

    for po in pos:

        cur.execute("""
        INSERT OR IGNORE INTO po
        (po_no,po_statement)
        VALUES (?,?)
        """, po)

    conn.commit()


# ---------------------------------------------------
# COURSE FUNCTIONS
# ---------------------------------------------------

def save_course(data):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM course")

    cur.execute("""
    INSERT INTO course
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
    VALUES (?,?,?,?,?,?,?,?)
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


# ---------------------------------------------------
# CO FUNCTIONS
# ---------------------------------------------------

def get_all_cos():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM co ORDER BY id")

    rows = cur.fetchall()

    conn.close()

    return rows


def add_co(statement, bloom):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM co")

    count = cur.fetchone()[0] + 1

    co_no = f"CO{count}"

    cur.execute("""
    INSERT INTO co
    (co_no,co_statement,bloom_level)
    VALUES (?,?,?)
    """, (co_no, statement, bloom))

    conn.commit()
    conn.close()


def update_co(co_id, statement, bloom):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE co
    SET
        co_statement=?,
        bloom_level=?
    WHERE id=?
    """, (statement, bloom, co_id))

    conn.commit()
    conn.close()


def delete_co(co_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM co WHERE id=?", (co_id,))

    conn.commit()
    conn.close()


def get_co(co_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM co WHERE id=?", (co_id,))

    row = cur.fetchone()

    conn.close()

    return row