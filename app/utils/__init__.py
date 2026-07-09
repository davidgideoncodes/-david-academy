def generate_student_id(year, month, existing_ids, school_code="FGC", class_name=None):

    year_part = str(year)[-2:]
    month_part = str(month).zfill(2)

    # convert class name to short code
    # JSS1 → J1, JSS2 → J2, SS1 → S1, SS3 → S3
    class_codes = {
        "JSS1": "J1", "JSS2": "J2", "JSS3": "J3",
        "SS1": "S1", "SS2": "S2", "SS3": "S3"
    }
    class_code = class_codes.get(class_name, "XX")

    # full prefix includes school, class, year, month
    # e.g. FGC-J1-2607
    prefix = f"{school_code}-{class_code}-{year_part}{month_part}"

    # only count existing IDs that match this exact prefix
    # so JSS1 and JSS2 each count from 001 independently
    existing_numbers = []
    for sid in existing_ids:
        if sid.startswith(prefix):
            number_part = sid[-3:]
            existing_numbers.append(int(number_part))

    if existing_numbers:
        next_number = max(existing_numbers) + 1
    else:
        next_number = 1

    number_part = str(next_number).zfill(3)
    return f"{prefix}{number_part}"