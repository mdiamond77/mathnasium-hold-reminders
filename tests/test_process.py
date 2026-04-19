import pandas as pd
import pytest
from process import filter_holds, split_by_center


@pytest.fixture
def holds_df():
    return pd.DataFrame({
        "Student Name":   ["Alice Smith",    "Bob Jones",     "Carol White",   "Dave Brown"],
        "Hold End Date":  ["4/30/2026",      "4/15/2026",     "5/31/2026",     "4/30/2026"],
        "Guardian Name":  ["Amy Smith",      "Bill Jones",    "Clara White",   "Dan Brown"],
        "Guardian Phone": ["(201) 555-0001", "(201) 555-0002","(201) 555-0003","(201) 555-0004"],
        "Guardian Email": ["amy@ex.com",     "bill@ex.com",   "clara@ex.com",  "dan@ex.com"],
        "Center Name":    ["Englewood",      "Teaneck",       "Englewood",     "Teaneck"],
    })


# ── filter_holds ──────────────────────────────────────────────────────────────

def test_filter_holds_returns_current_month(holds_df):
    result = filter_holds(holds_df, month=4, year=2026)
    names = [r["name"] for r in result]
    assert "Alice Smith" in names
    assert "Bob Jones" in names
    assert "Dave Brown" in names
    assert "Carol White" not in names  # May end date


def test_filter_holds_excludes_wrong_year(holds_df):
    result = filter_holds(holds_df, month=4, year=2025)
    assert result == []


def test_filter_holds_formats_end_date(holds_df):
    result = filter_holds(holds_df, month=4, year=2026)
    alice = next(r for r in result if r["name"] == "Alice Smith")
    assert alice["hold_end_date"] == "4/30/2026"


def test_filter_holds_includes_contact_info(holds_df):
    result = filter_holds(holds_df, month=4, year=2026)
    alice = next(r for r in result if r["name"] == "Alice Smith")
    assert alice["guardian_name"] == "Amy Smith"
    assert alice["guardian_phone"] == "(201) 555-0001"
    assert alice["guardian_email"] == "amy@ex.com"


def test_filter_holds_sorted_by_center_then_name(holds_df):
    result = filter_holds(holds_df, month=4, year=2026)
    keys = [(r["center"], r["name"]) for r in result]
    assert keys == sorted(keys)


# ── split_by_center ───────────────────────────────────────────────────────────

def test_split_by_center_all_centers_present_when_empty():
    result = split_by_center([])
    assert "Englewood" in result
    assert "Teaneck" in result


def test_split_by_center_splits_correctly(holds_df):
    holds = filter_holds(holds_df, month=4, year=2026)
    result = split_by_center(holds)
    assert len(result["Englewood"]) == 1   # Alice
    assert len(result["Teaneck"]) == 2     # Bob, Dave


def test_split_by_center_empty_center_is_empty_list(holds_df):
    # Filter for a month with only Englewood holds
    df = holds_df[holds_df["Center Name"] == "Englewood"].copy()
    df["Hold End Date"] = "4/30/2026"
    holds = filter_holds(df, month=4, year=2026)
    result = split_by_center(holds)
    assert result["Teaneck"] == []
