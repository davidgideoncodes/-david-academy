# app/utils/id_generator.py
# This file has ONE job: generate the next student ID
# Example output: FGC-2609001

def generate_student_id(year, month, existing_ids, school_code="FGC"):
    """
    year        → the full enrollment year e.g. 2026
    month       → the enrollment month as a number e.g. 9 for September
    existing_ids → a list of IDs already in the system, so we know what number comes next
    school_code  → prefix for the school, default is FGC
    """

    # Take last 2 digits of year: 2026 → "26"
    year_part = str(year)[-2:]

    # Make month always 2 digits: 9 → "09", 11 → "11"
    month_part = str(month).zfill(2)

    # Build the prefix this batch of students share e.g. "FGC-2609"
    prefix = f"{school_code}-{year_part}{month_part}"

    # Look through existing IDs and find ones that start with this same prefix
    # Then extract just the number at the end e.g. "FGC-2609003" → 3
    existing_numbers = []
    for student_id in existing_ids:
        if student_id.startswith(prefix):
            number_part = student_id[-3:]        # last 3 characters
            existing_numbers.append(int(number_part))

    # If no students enrolled this month yet, start at 1
    # Otherwise take the highest number and add 1
    if existing_numbers:
        next_number = max(existing_numbers) + 1
    else:
        next_number = 1

    # Format the number as 3 digits: 1 → "001", 12 → "012"
    number_part = str(next_number).zfill(3)

    # Put it all together
    return f"{prefix}{number_part}"