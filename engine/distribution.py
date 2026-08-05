"""
Distribution Business Logic
OBE Analytics Pro v1.1
"""

from database.co_distribution import save_distribution


def validate_distribution(matrix):
    """
    Validate that:
    LE = 25
    S1 = 30
    S2 = 45
    """

    expected = {
        "LE": 25,
        "S1": 30,
        "S2": 45
    }

    errors = []

    for assessment, expected_total in expected.items():

        total = sum(matrix.get(assessment, {}).values())

        if total != expected_total:
            errors.append(
                f"{assessment} total should be {expected_total}. Current total = {total}"
            )

    return errors


def matrix_to_rows(matrix):
    """
    Convert matrix into database rows.

    Example:

    {
        "LE":{"CO1":5,"CO2":5},
        "S1":{"CO1":15}
    }

    becomes

    [
        ("LE","CO1",5),
        ("LE","CO2",5),
        ("S1","CO1",15)
    ]
    """

    rows = []

    for assessment, cos in matrix.items():

        for co, marks in cos.items():

            rows.append(
                (
                    assessment,
                    co,
                    float(marks)
                )
            )

    return rows


def save_course_distribution(course_code, matrix):

    errors = validate_distribution(matrix)

    if errors:
        return False, errors

    rows = matrix_to_rows(matrix)

    save_distribution(course_code, rows)

    return True, ["Distribution saved successfully."]