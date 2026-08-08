"""
=========================================================
OBE Analytics
calculations.py
Calculation Engine
=========================================================
"""

# --------------------------------------------------------
# Calculate Total Marks
# --------------------------------------------------------

def calculate_total_marks(
    ce,
    s1,
    s2
):
    """
    Calculate total marks obtained by a student.
    """

    return ce + s1 + s2


# --------------------------------------------------------
# Calculate Percentage
# --------------------------------------------------------

def calculate_percentage(
    marks,
    maximum_marks
):
    """
    Convert marks into percentage.
    """

    if maximum_marks <= 0:
        return 0.0

    return (
        marks / maximum_marks
    ) * 100.0
# --------------------------------------------------------
# Calculate Direct CO Attainment
# --------------------------------------------------------

def calculate_direct_attainment(
    marks_obtained,
    maximum_marks
):
    """
    Calculate direct attainment percentage.

    Example:
        Marks Obtained = 72
        Maximum Marks  = 100

        Direct Attainment = 72%
    """

    if maximum_marks <= 0:
        return 0.0

    return (
        marks_obtained /
        maximum_marks
    ) * 100.0
# --------------------------------------------------------
# Calculate CO Attainment
# --------------------------------------------------------

def calculate_co_attainment(
    scores,
    target_percentage=60.0
):
    """
    Calculate CO attainment percentage.

    scores:
        List of student percentages for the CO.

    target_percentage:
        Minimum percentage required for CO attainment.

    Returns:
        Percentage of students who achieved
        the target.
    """

    if not scores:
        return 0.0

    total_students = len(scores)

    achieved_students = sum(
        1
        for score in scores
        if score >= target_percentage
    )

    return (
        achieved_students /
        total_students
    ) * 100.0
# --------------------------------------------------------
# Calculate Final CO Attainment
# --------------------------------------------------------

def calculate_final_co_attainment(
    direct_attainment,
    indirect_attainment=0.0,
    use_indirect=True,
    direct_weight=80.0,
    indirect_weight=20.0
):
    """
    Calculate final CO attainment using
    direct and optional indirect attainment.

    If indirect attainment is disabled,
    direct attainment is automatically treated as 100%.

    Returns:
        Final CO attainment percentage.
    """

    if not use_indirect:

        return float(direct_attainment)

    final_attainment = (
        direct_attainment *
        (direct_weight / 100.0)
    ) + (
        indirect_attainment *
        (indirect_weight / 100.0)
    )

    return final_attainment
# --------------------------------------------------------
# Calculate PO Attainment
# --------------------------------------------------------

def calculate_po_attainment(
    co_attainments,
    po_mapping
):
    """
    Calculate PO attainment using CO attainments
    and CO-PO mapping levels.

    Parameters
    ----------
    co_attainments : dict
        CO attainment percentages.

        Example:
        {
            1: 70.0,
            2: 80.0,
            3: 65.0,
            4: 75.0,
            5: 90.0
        }

    po_mapping : dict
        Mapping level for each CO to the selected PO.

        Example:
        {
            1: 3,
            2: 1,
            3: 0,
            4: 2,
            5: 0
        }

    Returns
    -------
    float
        PO attainment percentage.
    """

    weighted_sum = 0.0
    total_mapping = 0.0

    for co_no, mapping_level in po_mapping.items():

        mapping_level = float(mapping_level)

        if mapping_level <= 0:
            continue

        attainment = float(
            co_attainments.get(
                co_no,
                0.0
            )
        )

        weighted_sum += (
            attainment *
            mapping_level
        )

        total_mapping += mapping_level

    if total_mapping == 0:

        return 0.0

    return (
        weighted_sum /
        total_mapping
    )
# --------------------------------------------------------
# Calculate Course CO Attainment
# --------------------------------------------------------

def calculate_course_co_attainment(
    student_co_scores,
    target_percentage=60.0
):
    """
    Calculate attainment for all 5 COs.

    Parameters
    ----------
    student_co_scores : dict

        Example:

        {
            1: [70, 80, 55, 65, 40],
            2: [75, 85, 60, 70, 50],
            3: [80, 90, 70, 75, 65],
            4: [60, 70, 55, 80, 72],
            5: [90, 85, 75, 80, 88]
        }

        Key   = CO number
        Value = student percentages for that CO

    target_percentage : float
        Minimum percentage required for attainment.

    Returns
    -------
    dict
        CO attainment percentages.
    """

    co_attainment = {}

    for co_no, scores in student_co_scores.items():

        co_attainment[co_no] = calculate_co_attainment(
            scores,
            target_percentage
        )

    return co_attainment
# --------------------------------------------------------
# Calculate Course CO Attainment
# --------------------------------------------------------

def calculate_course_co_attainment(
    student_co_scores,
    target_percentage=60.0
):
    """
    Calculate attainment for all COs.

    student_co_scores:
        {
            1: [student percentages for CO1],
            2: [student percentages for CO2],
            ...
            5: [student percentages for CO5]
        }

    Returns:
        Dictionary containing CO attainment percentages.
    """

    co_attainment = {}

    for co_no, scores in student_co_scores.items():

        co_attainment[co_no] = calculate_co_attainment(
            scores,
            target_percentage
        )

    return co_attainment
# --------------------------------------------------------
# Calculate Final Attainment for All COs
# --------------------------------------------------------

def calculate_final_course_co_attainment(
    direct_co_attainment,
    indirect_co_attainment=None,
    use_indirect=True,
    direct_weight=80.0,
    indirect_weight=20.0
):
    """
    Calculate final attainment for all COs.

    Parameters
    ----------
    direct_co_attainment : dict
        Direct attainment for each CO.

        Example:
        {
            1: 70.0,
            2: 75.0,
            3: 80.0,
            4: 65.0,
            5: 90.0
        }

    indirect_co_attainment : dict or None
        Indirect attainment for each CO.

    use_indirect : bool
        True  -> Direct + Indirect
        False -> Direct becomes 100%

    direct_weight : float
        Direct contribution percentage.

    indirect_weight : float
        Indirect contribution percentage.

    Returns
    -------
    dict
        Final CO attainment percentages.
    """

    final_attainment = {}

    if indirect_co_attainment is None:

        indirect_co_attainment = {}

    for co_no, direct_value in direct_co_attainment.items():

        indirect_value = indirect_co_attainment.get(
            co_no,
            0.0
        )

        final_attainment[co_no] = calculate_final_co_attainment(
            direct_attainment=direct_value,
            indirect_attainment=indirect_value,
            use_indirect=use_indirect,
            direct_weight=direct_weight,
            indirect_weight=indirect_weight
        )

    return final_attainment