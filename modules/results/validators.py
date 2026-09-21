"""
Parse a normal_range string like "70 - 100" or "< 5" or "> 40" or "Negative"
and decide if a given result is normal, abnormal, or unknown.
"""
import re


def _try_float(value):
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def check_result(normal_range: str, result_value: str):
    """
    Returns one of: 'normal', 'abnormal', 'unknown'
    """
    if not normal_range or result_value in (None, ''):
        return 'unknown'

    normal_range = normal_range.strip()
    result_value = str(result_value).strip()

    # --- Case 1: Range like "70 - 100" or "70-100" ---
    m = re.match(r'^\s*(-?\d+(?:\.\d+)?)\s*[-–]\s*(-?\d+(?:\.\d+)?)\s*$', normal_range)
    if m:
        low, high = float(m.group(1)), float(m.group(2))
        val = _try_float(result_value)
        if val is None:
            return 'unknown'
        return 'normal' if low <= val <= high else 'abnormal'

    # --- Case 2: "< 5" or "≤ 5" ---
    m = re.match(r'^\s*[<≤]\s*(-?\d+(?:\.\d+)?)\s*$', normal_range)
    if m:
        bound = float(m.group(1))
        val = _try_float(result_value)
        if val is None:
            return 'unknown'
        return 'normal' if val < bound else 'abnormal'

    # --- Case 3: "> 40" or "≥ 40" ---
    m = re.match(r'^\s*[>≥]\s*(-?\d+(?:\.\d+)?)\s*$', normal_range)
    if m:
        bound = float(m.group(1))
        val = _try_float(result_value)
        if val is None:
            return 'unknown'
        return 'normal' if val > bound else 'abnormal'

    # --- Case 4: Textual (e.g. "Negative", "No growth") ---
    nr_lower = normal_range.lower()
    rv_lower = result_value.lower()
    if nr_lower in ('negative', 'normal', 'no growth', 'nil'):
        return 'normal' if nr_lower == rv_lower or rv_lower in ('', 'nil') else 'abnormal'

    # --- Fallback ---
    return 'unknown'