import pandas as pd

from config import (
    COL_STUDENT_NAME,
    COL_HOLD_END_DATE,
    COL_GUARDIAN_NAME,
    COL_GUARDIAN_PHONE,
    COL_GUARDIAN_EMAIL,
    COL_CENTER,
    CENTERS,
)


def filter_holds(df: pd.DataFrame, month: int, year: int) -> list[dict]:
    """Return holds where Hold End Date is in the given month and year.

    Returns list of dicts: {name, hold_end_date, guardian_name, guardian_phone,
    guardian_email, center}. Sorted by center then name.
    """
    results = []
    for _, row in df.iterrows():
        end_date = pd.to_datetime(row[COL_HOLD_END_DATE], errors='coerce')
        if pd.isna(end_date):
            continue
        if end_date.month == month and end_date.year == year:
            results.append({
                "name": row[COL_STUDENT_NAME],
                # Format as M/D/YYYY without zero-padding to match Radius export display
                "hold_end_date": "{}/{}/{}".format(
                    end_date.month, end_date.day, end_date.year
                ),
                "guardian_name": row[COL_GUARDIAN_NAME],
                "guardian_phone": row[COL_GUARDIAN_PHONE],
                "guardian_email": row[COL_GUARDIAN_EMAIL],
                "center": row[COL_CENTER],
            })
    return sorted(results, key=lambda x: (x["center"], x["name"]))


def split_by_center(holds: list[dict]) -> dict:
    """Split hold list into {center_name: [hold dicts]}.

    All CENTERS keys are always present (empty list if no holds for that center).
    """
    result = {center: [] for center in CENTERS}
    for hold in holds:
        center = hold["center"]
        if center in result:
            result[center].append(hold)
    return result


def process(holds_path, month: int, year: int) -> dict:
    """Load Holds Report Excel, filter by month/year, split by center.

    Returns {center_name: [hold dicts]} for all centers in CENTERS.
    Raises ValueError if the report is empty.
    """
    df = pd.read_excel(holds_path)
    if df.empty:
        raise ValueError("Holds report is empty — check Radius export and re-run.")
    holds = filter_holds(df, month, year)
    return split_by_center(holds)
