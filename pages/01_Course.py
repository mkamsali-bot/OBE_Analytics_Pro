
# OBE Analytics Pro v1.3
# 01_Course.py
# STEP 1 - ACTIVE COURSE FIX

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import streamlit as st


st.set_page_config(
    page_title="OBE Analytics Pro – Course",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_CANDIDATES = [
    BASE_DIR / "database" / "obe.db",
    BASE_DIR / "database" / "obe_analytics.db",
    BASE_DIR / "database" / "obe_analytics_pro.db",
    BASE_DIR / "obe.db",
    BASE_DIR / "obe_analytics.db",
    BASE_DIR / "data" / "obe.db",
    BASE_DIR / "data" / "obe_analytics.db",
]


def get_database_path() -> Path:
    for path in DATABASE_CANDIDATES:
        if path.exists():
            return path
    return BASE_DIR / "database" / "obe.db"


@st.cache_resource
def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def get_tables(conn: sqlite3.Connection) -> List[str]:
    sql = (
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
        "ORDER BY name"
    )
    rows = conn.execute(sql).fetchall()
    return [str(row["name"]) for row in rows]


def get_columns(conn: sqlite3.Connection, table_name: str) -> List[str]:
    rows = conn.execute(
        f'PRAGMA table_info("{table_name}")'
    ).fetchall()
    return [str(row["name"]) for row in rows]


def find_course_table(conn: sqlite3.Connection) -> Optional[str]:
    tables = get_tables(conn)
    lower_map = {table.lower(): table for table in tables}

    for name in (
        "course",
        "courses",
        "course_master",
        "course_master_data",
    ):
        if name in lower_map:
            return lower_map[name]

    for table in tables:
        columns = {c.lower() for c in get_columns(conn, table)}
        if (
            ("course_code" in columns or "code" in columns)
            and ("course_name" in columns or "name" in columns)
        ):
            return table

    return None


def find_column(
    columns: Sequence[str],
    candidates: Sequence[str],
) -> Optional[str]:
    lower_map = {column.lower(): column for column in columns}
    for candidate in candidates:
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]
    return None


def normalize_active_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0

    text = str(value).strip().lower()

    if text in {
        "1", "true", "yes", "y", "active",
        "enabled", "current"
    }:
        return True

    if text in {
        "0", "false", "no", "n", "inactive",
        "disabled", "closed"
    }:
        return False

    return True


def course_display_label(course: Dict[str, Any]) -> str:
    code = (
        course.get("course_code")
        or course.get("code")
        or course.get("course_no")
        or ""
    )

    name = (
        course.get("course_name")
        or course.get("name")
        or course.get("course_title")
        or ""
    )

    semester = (
        course.get("semester")
        or course.get("term")
        or ""
    )

    parts = [
        str(value).strip()
        for value in (code, name)
        if str(value).strip()
    ]

    label = " – ".join(parts)

    if semester:
        label = f"{label} | {semester}" if label else str(semester)

    return label or f"Course ID: {course.get('__course_id__', 'Unknown')}"


def load_courses(
    conn: sqlite3.Connection,
    table_name: str,
) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:

    columns = get_columns(conn, table_name)

    id_col = find_column(
        columns,
        ["id", "course_id"],
    )

    code_col = find_column(
        columns,
        ["course_code", "code", "course_no", "course_number"],
    )

    name_col = find_column(
        columns,
        ["course_name", "name", "course_title", "title"],
    )

    semester_col = find_column(
        columns,
        ["semester", "term"],
    )

    academic_year_col = find_column(
        columns,
        ["academic_year", "ay", "year"],
    )

    active_col = find_column(
        columns,
        ["is_active", "active", "status", "course_status"],
    )

    if id_col is None:
        id_expression = "rowid AS __course_id__"
    else:
        id_expression = f'"{id_col}" AS __course_id__'

    order_column = code_col or name_col or id_col or "rowid"

    query = (
        f'SELECT {id_expression}, * '
        f'FROM "{table_name}" '
        f'ORDER BY "{order_column}"'
    )

    rows = conn.execute(query).fetchall()

    courses: List[Dict[str, Any]] = []

    for row in rows:
        raw = dict(row)

        if active_col is not None:
            if not normalize_active_value(raw.get(active_col)):
                continue

        record = dict(raw)

        record["course_code"] = (
            raw.get(code_col) if code_col else ""
        )

        record["course_name"] = (
            raw.get(name_col) if name_col else ""
        )

        record["semester"] = (
            raw.get(semester_col) if semester_col else ""
        )

        record["academic_year"] = (
            raw.get(academic_year_col)
            if academic_year_col
            else ""
        )

        record["display_label"] = course_display_label(record)

        courses.append(record)

    column_map = {
        "id": id_col or "",
        "code": code_col or "",
        "name": name_col or "",
        "semester": semester_col or "",
        "academic_year": academic_year_col or "",
        "active": active_col or "",
    }

    return courses, column_map


SESSION_COURSE_ID = "active_course_id"
SESSION_COURSE = "active_course"
SESSION_COURSE_LABEL = "active_course_label"


def set_active_course(course: Dict[str, Any]) -> None:
    st.session_state[SESSION_COURSE_ID] = course.get(
        "__course_id__"
    )
    st.session_state[SESSION_COURSE] = course
    st.session_state[SESSION_COURSE_LABEL] = course.get(
        "display_label",
        course_display_label(course),
    )


def get_active_course() -> Optional[Dict[str, Any]]:
    return st.session_state.get(SESSION_COURSE)


def render_header() -> None:
    st.title("🎓 Course Management")
    st.caption(
        "OBE Analytics Pro v1.3 · STEP 1 – Active Course Fix"
    )


def render_database_status(
    db_path: Path,
    table_name: Optional[str],
    courses: Sequence[Dict[str, Any]],
) -> None:

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Database", db_path.name)

    with col2:
        st.metric("Course Table", table_name or "Not found")

    with col3:
        st.metric("Active Courses", len(courses))


def render_active_course_banner(
    course: Optional[Dict[str, Any]]
) -> None:

    if not course:
        st.info("No active course is selected.")
        return

    label = course.get(
        "display_label",
        course_display_label(course),
    )

    st.success(f"**Active Course:** {label}")


def render_course_details(
    course: Dict[str, Any]
) -> None:

    st.subheader("Selected Course")

    preferred_fields = [
        ("Course Code", "course_code"),
        ("Course Name", "course_name"),
        ("Semester", "semester"),
        ("Academic Year", "academic_year"),
    ]

    values = []

    for title, key in preferred_fields:
        value = course.get(key)
        if value not in (None, ""):
            values.append((title, value))

    if values:
        cols = st.columns(min(4, len(values)))

        for index, (title, value) in enumerate(values):
            with cols[index % len(cols)]:
                st.metric(title, str(value))

    with st.expander("Course Record", expanded=False):
        visible = {
            key: value
            for key, value in course.items()
            if not key.startswith("__")
            and key != "display_label"
        }
        st.json(visible)


def render_course_selector(
    courses: Sequence[Dict[str, Any]]
) -> None:

    if not courses:
        st.warning(
            "No active courses were found. "
            "Please create or activate a course "
            "in the database before continuing."
        )
        return

    labels = [course["display_label"] for course in courses]

    existing_id = st.session_state.get(SESSION_COURSE_ID)
    default_index = 0

    if existing_id is not None:
        for index, course in enumerate(courses):
            if course.get("__course_id__") == existing_id:
                default_index = index
                break

    selected_label = st.selectbox(
        "Select Active Course",
        labels,
        index=default_index,
        key="course_selector_v13",
    )

    selected_course = next(
        (
            course
            for course in courses
            if course["display_label"] == selected_label
        ),
        None,
    )

    if selected_course is not None:
        set_active_course(selected_course)

    active_course = get_active_course()

    st.divider()
    render_active_course_banner(active_course)

    if active_course:
        render_course_details(active_course)


def main() -> None:
    render_header()

    db_path = get_database_path()

    try:
        db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        conn = get_connection(str(db_path))

    except Exception as exc:
        st.error("Unable to open the OBE database.")
        st.exception(exc)
        return

    table_name = find_course_table(conn)

    if table_name is None:
        st.error(
            "The Course table was not found in the current database."
        )

        st.info(
            "Initialize the OBE Analytics Pro database first, "
            "then reopen this page."
        )

        with st.expander("Database diagnostic information"):
            st.write("Database path:", str(db_path))
            st.write("Tables detected:", get_tables(conn))

        return

    try:
        courses, column_map = load_courses(
            conn,
            table_name,
        )

    except Exception as exc:
        st.error("The Course table could not be read.")
        st.exception(exc)
        return

    render_database_status(
        db_path,
        table_name,
        courses,
    )

    with st.expander(
        "Detected Course Schema",
        expanded=False,
    ):
        st.json(column_map)

    st.divider()
    render_course_selector(courses)


if __name__ == "__main__":
    main()
