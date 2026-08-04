"""
Course Outcomes Database Functions
OBE Analytics Pro v1.0.0
"""

from database.connection import get_connection


def save_all_cos(data):
    """
    Save all Course Outcomes.

    Parameters:
        data = [
            ("CO1", "Understand antenna fundamentals", "L2"),
            ("CO2", "Analyze radiation characteristics", "L4"),
            ...
        ]
    """

    conn = get_connection()
    cur = conn.cursor()

    # Remove existing COs
    cur.execute("DELETE FROM co")

    # Insert new COs
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


def get_all_cos():
    """
    Returns all Course Outcomes.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            co_no,
            co_statement,
            bloom_level
        FROM co
        ORDER BY id
    """)

    rows = cur.fetchall()

    conn.close()

    return rows


def delete_all_cos():
    """
    Delete all Course Outcomes.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM co")

    conn.commit()
    conn.close()