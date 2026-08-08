"""
=========================================================
OBE Analytics
database.py
---------------------------------------------------------
SQLite Database Module
=========================================================
"""

import sqlite3
from pathlib import Path

DB_NAME = "obe.db"


# --------------------------------------------------------
# Database Connection
# --------------------------------------------------------

def get_connection():
    """Return SQLite database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------------------------------------
# Initialize Database
# --------------------------------------------------------

def initialize_database():
    """Create database tables if they do not exist."""
    
    conn = get_connection()
    cur = conn.cursor()

    # =====================================================
    # COURSE
    # =====================================================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS course(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT UNIQUE NOT NULL,
        course_name TEXT NOT NULL,
        faculty TEXT,
        semester TEXT,
        academic_year TEXT,

        ce_max INTEGER DEFAULT 25,
        s1_max INTEGER DEFAULT 30,
        s2_max INTEGER DEFAULT 45,

        use_indirect INTEGER DEFAULT 1,
        direct_weight REAL DEFAULT 80,
        indirect_weight REAL DEFAULT 20
    )
    """)

    # =====================================================
    # COURSE OUTCOMES
    # =====================================================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS co(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,
        co_no INTEGER,
        co_statement TEXT,
        bloom_level TEXT,

        FOREIGN KEY(course_id) REFERENCES course(id)
    )
    """)

    # =====================================================
    # STUDENT MARKS
    # =====================================================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS marks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,

        student_id TEXT,
        student_name TEXT,

        ce REAL,
        s1 REAL,
        s2 REAL,

        FOREIGN KEY(course_id) REFERENCES course(id)
    )
    """)

    # =====================================================
    # CO-WISE STUDENT MARKS
    # =====================================================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS co_marks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        student_id TEXT NOT NULL,
        co_no INTEGER NOT NULL,
        marks REAL DEFAULT 0,

        FOREIGN KEY(course_id) REFERENCES course(id),
        UNIQUE(course_id, student_id, co_no)
    )
    """)

    # =====================================================
    # CO-PO MAPPING
    # =====================================================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS mapping(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,
        co_no INTEGER,
        po_no INTEGER,
        mapping_level INTEGER,

        FOREIGN KEY(course_id) REFERENCES course(id)
    )
    """)

    # =====================================================
    # CO ATTAINMENT
    # =====================================================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS co_attainment(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,
        co_no INTEGER,
        attainment REAL,

        FOREIGN KEY(course_id) REFERENCES course(id)
    )
    """)

    # =====================================================
    # COURSE EXIT SURVEY
    # =====================================================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS survey(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,
        po_no INTEGER,
        survey_score REAL,

        FOREIGN KEY(course_id) REFERENCES course(id)
    )
    """)

    # =====================================================
    # PO ATTAINMENT
    # =====================================================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS po_attainment(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,
        po_no INTEGER,
        direct REAL,
        indirect REAL,
        final REAL,

        FOREIGN KEY(course_id) REFERENCES course(id)
    )
    """)

    # =====================================================
    # SETTINGS
    # =====================================================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings(
        id INTEGER PRIMARY KEY,
        active_course_id INTEGER
    )
    """)

    cur.execute("""
    INSERT OR IGNORE INTO settings(id, active_course_id)
    VALUES(1, NULL)
    """)

    conn.commit()
    conn.close()


# --------------------------------------------------------
# Execute INSERT / UPDATE / DELETE
# --------------------------------------------------------

def execute_query(query, values=()):
    """Execute INSERT, UPDATE or DELETE query."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(query, values)

    conn.commit()
    conn.close()


# --------------------------------------------------------
# Fetch One Record
# --------------------------------------------------------

def fetch_one(query, values=()):
    """Return one record."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(query, values)
    row = cur.fetchone()

    conn.close()
    return row


# --------------------------------------------------------
# Fetch All Records
# --------------------------------------------------------

def fetch_all(query, values=()):
    """Return all matching records."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(query, values)
    rows = cur.fetchall()

    conn.close()
    return rows


# --------------------------------------------------------
# Insert and Return ID
# --------------------------------------------------------

def insert_data(query, values=()):
    """Insert record and return last inserted ID."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(query, values)
    last_id = cur.lastrowid

    conn.commit()
    conn.close()

    return last_id


# --------------------------------------------------------
# Update Record
# --------------------------------------------------------

def update_data(query, values=()):
    """Update existing records."""
    execute_query(query, values)


# --------------------------------------------------------
# Delete Record
# --------------------------------------------------------

def delete_data(query, values=()):
    """Delete records."""
    execute_query(query, values)


# --------------------------------------------------------
# Fetch Data as DataFrame
# --------------------------------------------------------

def fetch_dataframe(query, values=()):
    """Return query result as a Pandas DataFrame."""
    import pandas as pd

    conn = get_connection()

    df = pd.read_sql_query(
        query,
        conn,
        params=values
    )

    conn.close()
    return df


# --------------------------------------------------------
# Set Active Course
# --------------------------------------------------------

def set_active_course(course_id):
    """Store active course."""
    execute_query(
        """
        UPDATE settings
        SET active_course_id=?
        WHERE id=1
        """,
        (course_id,)
    )


# --------------------------------------------------------
# Get Active Course
# --------------------------------------------------------

def get_active_course():
    """Return active course details."""
    return fetch_one(
        """
        SELECT
            c.*
        FROM course c
        JOIN settings s
            ON c.id = s.active_course_id
        WHERE s.id = 1
        """
    )


# --------------------------------------------------------
# Main
# --------------------------------------------------------

if __name__ == "__main__":
    initialize_database()

    print("=" * 45)
    print("OBE Analytics Database Created Successfully")
    print(f"Database : {Path(DB_NAME).resolve()}")
    print("=" * 45)