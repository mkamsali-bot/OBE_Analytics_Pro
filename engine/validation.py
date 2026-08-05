"""
Validation Module
OBE Analytics Pro v1.1
"""


def validate_student_marks(le, s1, s2):
    """
    Validate student assessment marks.
    """

    errors = []

    if le < 0 or le > 25:
        errors.append("LE marks must be between 0 and 25.")

    if s1 < 0 or s1 > 30:
        errors.append("Sessional-1 marks must be between 0 and 30.")

    if s2 < 0 or s2 > 45:
        errors.append("Sessional-2 marks must be between 0 and 45.")

    return errors


def validate_mapping(level):
    """
    CO-PO mapping must be 0,1,2 or 3
    """

    return level in [0, 1, 2, 3]


def validate_survey(value):
    """
    Survey attainment must be between 0 and 3
    """

    return 0 <= value <= 3


def validate_distribution(total, expected):
    """
    Validate assessment distribution totals.
    """

    return abs(total - expected) < 0.001