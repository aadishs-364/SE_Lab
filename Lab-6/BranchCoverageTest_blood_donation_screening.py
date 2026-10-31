import pytest
from blood_donation_screening import process_donor_cohort, verify_storage_centrifuge


def cohort(donors, registered=True, ctype="standard", fast_track=False):
    return {"clinic_registered": registered, "type": ctype,
            "fast_track": fast_track, "donors": donors}


GOOD = {"age": 25, "weight_kg": 65, "hb": 14.0}


# ---- Input validation: both sides of the `or` ----
def test_non_list_cohorts_raises():
    with pytest.raises(ValueError):
        process_donor_cohort("not a list", 450)


def test_non_positive_volume_raises():
    with pytest.raises(ValueError):
        process_donor_cohort([], 0)


def test_empty_cohort_list_zero_yield():
    # for-loop over cohorts executes zero times
    assert process_donor_cohort([], 450) == {"collected_ml": 0, "status": "ZERO_YIELD"}


# ---- clinic_registered True / False ----
def test_unregistered_cohort_skipped():
    result = process_donor_cohort([cohort([GOOD], registered=False)], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_missing_keys_use_defaults():
    # no "clinic_registered" -> skipped; registered with no donors/type -> defaults
    result = process_donor_cohort([{"donors": [GOOD]}, {"clinic_registered": True}], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


# ---- Accepted donor path, fast_track False ----
def test_single_accepted_donor():
    result = process_donor_cohort([cohort([GOOD])], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


# ---- Age / weight deferral (each side of the `or`) ----
def test_underage_deferred():
    result = process_donor_cohort([cohort([{"age": 16, "weight_kg": 65, "hb": 14.0}, GOOD])], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


def test_underweight_deferred():
    result = process_donor_cohort([cohort([{"age": 25, "weight_kg": 49, "hb": 14.0}])], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_age_and_weight_boundaries_accepted():
    result = process_donor_cohort([cohort([{"age": 17, "weight_kg": 50, "hb": 12.5}])], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


# ---- Hemoglobin branches ----
def test_low_hb_standard_cohort_continues():
    # low hb in a non high-altitude cohort: deferred, but loop continues
    donors = [{"age": 25, "weight_kg": 65, "hb": 12.0}, GOOD]
    result = process_donor_cohort([cohort(donors)], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


def test_low_hb_high_altitude_resets_and_breaks():
    donors = [GOOD, {"age": 30, "weight_kg": 70, "hb": 11.0}, GOOD]
    result = process_donor_cohort([cohort(donors, ctype="high_altitude")], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_high_altitude_reset_wipes_previous_cohorts():
    cohorts = [cohort([GOOD]), cohort([{"age": 30, "weight_kg": 70, "hb": 10.0}], ctype="high_altitude")]
    assert process_donor_cohort(cohorts, 450) == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_high_hb_deferred():
    result = process_donor_cohort([cohort([{"age": 25, "weight_kg": 65, "hb": 18.5}])], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_hb_upper_boundary_accepted():
    result = process_donor_cohort([cohort([{"age": 25, "weight_kg": 65, "hb": 18.0}])], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


# ---- fast_track ----
def test_fast_track_adds_bonus():
    result = process_donor_cohort([cohort([GOOD], fast_track=True)], 450)
    assert result == {"collected_ml": 500, "status": "ACCEPTED"}


def test_fast_track_only_bonus_is_accepted():
    result = process_donor_cohort([cohort([], fast_track=True)], 450)
    assert result == {"collected_ml": 50, "status": "ACCEPTED"}


# ---- Final status decisions ----
def test_high_deferral():
    donors = [{"age": 16, "weight_kg": 65, "hb": 14.0}] * 5 + [GOOD]
    result = process_donor_cohort([cohort(donors)], 450)
    assert result == {"collected_ml": 450, "status": "HIGH_DEFERRAL"}


def test_exactly_four_deferrals_not_high():
    donors = [{"age": 16, "weight_kg": 65, "hb": 14.0}] * 4 + [GOOD]
    result = process_donor_cohort([cohort(donors)], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


# ---- verify_storage_centrifuge ----
def test_centrifuge_no_data():
    assert verify_storage_centrifuge([]) == "NO_DATA"
    assert verify_storage_centrifuge(None) == "NO_DATA"


def test_centrifuge_abort_on_two_consecutive_drops():
    assert verify_storage_centrifuge([[3500, 2900, 2800]]) == "ABORT_SPIN"


def test_centrifuge_streak_resets_on_recovery():
    assert verify_storage_centrifuge([[2900, 3200, 2900, 3100]]) == "STABLE"


def test_centrifuge_streak_resets_between_runs():
    # drop at end of run 1 and start of run 2 must NOT combine
    assert verify_storage_centrifuge([[3500, 2900], [2900, 3500]]) == "STABLE"


def test_centrifuge_empty_run_and_boundary():
    assert verify_storage_centrifuge([[], [3000, 3000]]) == "STABLE"


def test_centrifuge_abort_in_later_run():
    assert verify_storage_centrifuge([[3500], [2000, 1000]]) == "ABORT_SPIN"
