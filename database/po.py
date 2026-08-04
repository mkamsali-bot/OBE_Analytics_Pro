"""
Program Outcomes Database Functions
OBE Analytics Pro v1.0.0
"""

from database.connection import get_connection


def preload_pos():
    """
    Insert NBA Program Outcomes (PO1-PO12)
    only if they do not already exist.
    """

    conn = get_connection()
    cur = conn.cursor()

    pos = [

        ("PO1", "Engineering knowledge"),

        ("PO2", "Problem analysis"),

        ("PO3", "Design/development of solutions"),

        ("PO4", "Conduct investigations of complex problems"),

        ("PO5", "Modern tool usage"),

        ("PO6", "The engineer and society"),

        ("PO7", "Environment and sustainability"),

        ("PO8", "Ethics"),

        ("PO9", "Individual and team work"),

        ("PO10", "Communication"),

        ("PO11", "Project management and finance"),

        ("PO12", "Life-long learning"),

    ]

    cur.executemany(
        """
        INSERT OR IGNORE INTO po(
            po_no,
            po_statement
        )
        VALUES(?,?)
        """,
        pos,
    )

    conn.commit()
    conn.close()


def get_all_pos():
    """
    Returns all Program Outcomes.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            po_no,
            po_statement
        FROM po
        ORDER BY id
    """)

    rows = cur.fetchall()

    conn.close()

    return rows