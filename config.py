"""
====================================================
OBE Analytics Pro
Configuration File
====================================================
"""

# -------------------------------
# Application
# -------------------------------

APP_NAME = "OBE Analytics Pro"

PAGE_TITLE = "OBE Analytics Pro"

PAGE_ICON = "🎓"

LAYOUT = "wide"

VERSION = "1.0"

# -------------------------------
# Institution
# -------------------------------

UNIVERSITY = "GITAM (Deemed to be University)"

SCHOOL = "School of Technology"

DEPARTMENT = "Department of EECE"

# -------------------------------
# Theme
# -------------------------------

PRIMARY_COLOR = "#0F4C81"

SECONDARY_COLOR = "#1976D2"

BACKGROUND_COLOR = "#F5F7FA"

CARD_COLOR = "#FFFFFF"

SUCCESS_COLOR = "#2E7D32"

WARNING_COLOR = "#ED6C02"

ERROR_COLOR = "#D32F2F"

# -------------------------------
# Navigation
# -------------------------------

MENU_ITEMS = [

    "🏠 Dashboard",

    "📘 Course",

    "🎯 Course Outcomes",

    "🎓 Program Outcomes",

    "🔗 CO-PO Mapping",

    "👁 Preview",

    "📄 Reports"

]

# -------------------------------
# Bloom's Levels
# -------------------------------

BLOOM_LEVELS = [

    "L1",
    "L2",
    "L3",
    "L4",
    "L5",
    "L6"

]

# -------------------------------
# Mapping Levels
# -------------------------------

MAPPING_LEVELS = [

    0,
    1,
    2,
    3

]

# -------------------------------
# Default Academic Year
# -------------------------------

DEFAULT_ACADEMIC_YEAR = "2026-27"

# -------------------------------
# Program Outcomes
# -------------------------------

TOTAL_POS = 12

# ==========================================================
# Assessment Configuration
# ==========================================================

# Assessment Pattern (Total = 100 Marks)
ASSESSMENT_PATTERN = {
    "LE": {
        "name": "Learning Evaluation",
        "marks": 25
    },
    "S1": {
        "name": "Sessional-1",
        "marks": 30
    },
    "S2": {
        "name": "Sessional-2",
        "marks": 45
    }
}

TOTAL_INTERNAL_MARKS = 100

# ==========================================================
# Attainment Configuration
# ==========================================================

# Final CO Attainment = 80% Direct + 20% Indirect
DIRECT_WEIGHT = 0.80

INDIRECT_WEIGHT = 0.20

# NBA Attainment Levels
ATTAINMENT_LEVELS = [0, 1, 2, 3]

# ==========================================================
# Course End Survey
# ==========================================================

SURVEY_MAX_SCORE = 3.0

# ==========================================================
# Number of Course Outcomes
# ==========================================================

TOTAL_COS = 6