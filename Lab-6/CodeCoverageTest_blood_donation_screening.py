import pytest
from blood_donation_screening import process_donor_cohort, verify_storage_centrifuge


def cohort(donors, registered=True, ctype="standard", fast_track=False):
    return {"clinic_registered": registered, "type": ctype,
            "fast_track": fast_track, "donors": donors}


def test_single_accepted_donor():
    result = process_donor_cohort([cohort([{"age": 25, "weight_kg": 65, "hb": 14.0}])], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


def test_invalid_input_raises():
    with pytest.raises(ValueError):
        process_donor_cohort("not a list", 450)


def test_unregistered_cohort_skipped():
    result = process_donor_cohort([cohort([{"age": 25, "weight_kg": 65, "hb": 14.0}], registered=False)], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_low_hb_high_altitude_resets_and_breaks():
    donors = [{"age": 25, "weight_kg": 65, "hb": 14.0}, {"age": 30, "weight_kg": 70, "hb": 11.0}]
    result = process_donor_cohort([cohort(donors, ctype="high_altitude")], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_high_deferral_with_fast_track():
    donors = [
        {"age": 16, "weight_kg": 65, "hb": 14.0},   # underage
        {"age": 25, "weight_kg": 45, "hb": 14.0},   # underweight
        {"age": 25, "weight_kg": 65, "hb": 19.0},   # hb too high
        {"age": 25, "weight_kg": 65, "hb": 18.5},   # hb too high
        {"age": 25, "weight_kg": 65, "hb": 18.1},   # hb too high
    ]
    result = process_donor_cohort([cohort(donors, fast_track=True)], 450)
    assert result == {"collected_ml": 50, "status": "HIGH_DEFERRAL"}


def test_centrifuge_no_data():
    assert verify_storage_centrifuge([]) == "NO_DATA"


def test_centrifuge_abort():
    assert verify_storage_centrifuge([[3500, 2900, 2800]]) == "ABORT_SPIN"


def test_centrifuge_stable():
    assert verify_storage_centrifuge([[3500, 2900, 3200]]) == "STABLE"
