from hypothesis import given, settings, strategies as st
from processor import validate_blood_type, calculate_pulse_pressure, parse_donor_registry

# Strategies: random text/None plus "almost valid" inputs that hit edge cases faster
blood_like = st.builds(lambda a, r: a + r,
                       st.sampled_from(["A", "B", "AB", "O", "", "X", " a"]),
                       st.sampled_from(["+", "-", "", "*", " "]))
bp_like = st.builds(lambda s, d, sep: f"{s}{sep}{d}",
                    st.integers(-300, 300), st.integers(-300, 300),
                    st.sampled_from(["/", "//", "", "\\"]))
donor_like = st.lists(st.text(max_size=6) | st.floats(allow_nan=True).map(str),
                      max_size=5).map("|".join)


@settings(max_examples=500)
@given(st.text() | st.none() | blood_like)
def test_validate_blood_type_no_crash(s):
    try:
        result = validate_blood_type(s)
        assert isinstance(result, str)
    except Exception as e:
        assert False, f"validate_blood_type crashed on {s!r} with: {type(e).__name__}: {e}"


@settings(max_examples=500)
@given(st.text() | st.none() | bp_like)
def test_calculate_pulse_pressure_safe(s):
    try:
        result = calculate_pulse_pressure(s)
        assert isinstance(result, str)
    except Exception as e:
        assert False, f"calculate_pulse_pressure crashed on {s!r} with: {type(e).__name__}: {e}"


@settings(max_examples=500)
@given(st.text() | st.none() | donor_like)
def test_parse_donor_registry_safe(s):
    try:
        result = parse_donor_registry(s)
        assert isinstance(result, str)
    except Exception as e:
        assert False, f"parse_donor_registry crashed on {s!r} with: {type(e).__name__}: {e}"
