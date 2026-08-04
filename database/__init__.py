"""
Database Package
"""

from database.connection import get_connection
from database.initialize import initialize_database

from database.course import (
    save_course,
    get_course,
    course_exists,
)