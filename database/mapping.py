"""
CO-PO Mapping Database Functions
OBE Analytics Pro v1.0.0
"""

from database.connection import get_connection


def delete_mapping():
    """
    Delete all CO-PO mappings.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM co_po_mapping")

    conn.commit()
    conn.close()


def save_mapping(data):
    """
    Save all CO-PO mappings.

    data format:
    [
        ("CO1", "PO1", 3),
        ("CO1", "PO2", 2),
        ("CO2", "PO1", 1),
        ...
    ]
    """

    conn = get_connection()
    cur = conn.cursor()

    # Remove old mappings
    cur.execute("DELETE FROM co_po_mapping")

    # Insert new mappings
    cur.executemany(
        """
        INSERT INTO co_po_mapping(
            co_no,
            po_no,
            level
        )
        VALUES (?, ?, ?)
        """,
        data,
    )

    conn.commit()
    conn.close()


def get_mapping():
    """
    Returns all saved mappings.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            co_no,
            po_no,
            level
        FROM co_po_mapping
        ORDER BY co_no, po_no
    """)

    rows = cur.fetchall()

    conn.close()

    return rows