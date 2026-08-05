"""
Marks Calculation Engine
OBE Analytics Pro v1.1
"""


def calculate_assessment_contribution(student_mark, assessment_max, allocated_mark):
    """
    Calculates CO contribution from one assessment.

    Formula:
    Contribution = (Student Marks / Assessment Max) × CO Allocated Marks
    """

    if assessment_max == 0:
        return 0

    return round((student_mark / assessment_max) * allocated_mark, 2)


def calculate_co_marks(le, s1, s2, distribution):
    """
    Calculate CO-wise marks.

    Parameters
    ----------
    le : float
    s1 : float
    s2 : float

    distribution : dictionary

    Example:

    {
        "CO1":{"LE":5,"S1":15,"S2":0},
        "CO2":{"LE":5,"S1":15,"S2":0},
        "CO3":{"LE":5,"S1":0,"S2":15},
        "CO4":{"LE":5,"S1":0,"S2":15},
        "CO5":{"LE":5,"S1":0,"S2":15}
    }

    """

    result = {}

    for co, marks in distribution.items():

        total = 0

        total += calculate_assessment_contribution(
            le,
            25,
            marks.get("LE", 0)
        )

        total += calculate_assessment_contribution(
            s1,
            30,
            marks.get("S1", 0)
        )

        total += calculate_assessment_contribution(
            s2,
            45,
            marks.get("S2", 0)
        )

        result[co] = round(total, 2)

    return result