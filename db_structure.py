import sqlite3

conn = sqlite3.connect("database/obe.db")
cursor = conn.cursor()

tables = [
    "co_po_mapping",
    "final_co_attainment",
    "course_end_survey",
    "po_attainment"
]

for table in tables:

    print("\n" + "=" * 60)
    print(f"TABLE : {table}")
    print("=" * 60)

    cursor.execute(f"PRAGMA table_info({table})")

    columns = cursor.fetchall()

    for column in columns:
        print(column)

conn.close()