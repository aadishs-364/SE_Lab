import math

VALID_ANTIGENS = {"A", "B", "AB", "O"}
RH_MAP = {"+": "Positive", "-": "Negative"}


def validate_blood_type(blood_code):
    """
    Standardizes blood group and Rh factor (e.g. 'O+', 'AB-').
    Returns an 'Error: ...' string for any invalid input instead of crashing.
    """
    if not isinstance(blood_code, str):
        return "Error: blood type must be a string"
    cleaned = blood_code.strip().upper().replace(" ", "")
    if len(cleaned) < 2:
        return "Error: blood type too short (expected e.g. 'O+')"
    antigen, rh_char = cleaned[:-1], cleaned[-1]
    if antigen not in VALID_ANTIGENS:
        return f"Error: invalid ABO antigen {antigen!r} (expected A, B, AB or O)"
    if rh_char not in RH_MAP:
        return f"Error: invalid Rh sign {rh_char!r} (expected + or -)"
    return f"{antigen} {RH_MAP[rh_char]}"


def calculate_pulse_pressure(bp_string):
    """
    Calculates pulse pressure (systolic - diastolic) and arterial ratio.
    Expects 'systolic/diastolic' (e.g. '120/80'); returns an error string otherwise.
    """
    if not isinstance(bp_string, str):
        return "Error: BP must be a string"
    parts = bp_string.strip().split('/')
    if len(parts) != 2:
        return "Error: BP must be in 'systolic/diastolic' format"
    try:
        systolic = int(parts[0].strip())
        diastolic = int(parts[1].strip())
    except ValueError:
        return "Error: systolic and diastolic must be whole numbers"
    if not (0 < systolic <= 300 and 0 < diastolic <= 300):
        return "Error: BP values must be between 1 and 300 mmHg"
    if diastolic >= systolic:
        return "Error: systolic must be greater than diastolic"
    pulse_diff = systolic - diastolic
    ratio = round(systolic / diastolic, 2)
    return f"Diff: {pulse_diff}, Ratio: {ratio}"


def parse_donor_registry(donor_entry):
    """
    Parses pipe-delimited record: 'DonorID|WeightKg|Hemoglobin'.
    Returns an error string for malformed records instead of crashing.
    """
    if not isinstance(donor_entry, str):
        return "Error: record must be a string"
    fields = donor_entry.split('|')
    if len(fields) != 3:
        return "Error: record must have exactly 3 fields 'ID|Weight|Hemoglobin'"
    donor_id = fields[0].strip()
    if not donor_id:
        return "Error: donor ID is empty"
    try:
        weight = float(fields[1])
        hemoglobin = float(fields[2])
    except ValueError:
        return "Error: weight and hemoglobin must be numbers"
    if not (math.isfinite(weight) and math.isfinite(hemoglobin)):
        return "Error: weight and hemoglobin must be finite numbers"
    if not (0 < weight <= 500):
        return "Error: weight must be between 0 and 500 kg"
    if not (0 < hemoglobin <= 25):
        return "Error: hemoglobin must be between 0 and 25 g/dL"
    eligible = weight >= 50.0 and hemoglobin >= 12.5
    return f"Donor {donor_id}: {'Eligible' if eligible else 'Deferred'}"


def main():
    print("==== Running validate_blood_type ====")
    b_input = input("Enter blood type (e.g. A+, O-, AB+): ")
    print("Validated:", validate_blood_type(b_input))

    print("\n==== Running calculate_pulse_pressure ====")
    bp_input = input("Enter BP (e.g. 120/80): ")
    print("BP Metrics:", calculate_pulse_pressure(bp_input))

    print("\n==== Running parse_donor_registry ====")
    d_input = input("Enter record (ID|Weight|Hemoglobin): ")
    print("Status:", parse_donor_registry(d_input))


if __name__ == "__main__":
    main()
