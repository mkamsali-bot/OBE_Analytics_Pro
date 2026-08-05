"""
Database Package
OBE Analytics Pro v1.1.2
"""

from database.connection import get_connection
from database.initialize import initialize_database

# ---------------------------------------------------------
# Course
# ---------------------------------------------------------

from database.course import (
    save_course,
    get_course,
    get_all_courses,
    update_course,
    delete_course,
    course_exists,
)

# ---------------------------------------------------------
# CO
# ---------------------------------------------------------

from database.co import (
    save_all_cos,
    get_all_cos,
    delete_all_cos,
)

# ---------------------------------------------------------
# PO
# ---------------------------------------------------------

from database.po import (
    preload_pos,
    get_all_pos,
)

# ---------------------------------------------------------
# CO-PO Mapping
# ---------------------------------------------------------

from database.mapping import (
    save_mapping,
    get_mapping,
    delete_mapping,
)

# ---------------------------------------------------------
# CO Distribution
# ---------------------------------------------------------

from database.co_distribution import (
    get_distribution,
    save_distribution,
    distribution_exists,
)

# ---------------------------------------------------------
# Student Marks
# ---------------------------------------------------------

from database.student_marks import (
    add_student_marks,
    update_student_marks,
    delete_student_marks,
    get_student_marks,
    get_students_by_course,
    save_bulk_marks,
    clear_course_marks,
)