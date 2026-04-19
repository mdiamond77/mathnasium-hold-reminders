import calendar
import os
from pathlib import Path

import pandas as pd
from playwright.sync_api import sync_playwright

from config import INPUT_DIR, RADIUS_LOGIN_URL, HOLDS_REPORT_URL


def _login(page) -> None:
    """Log into Radius."""
    username = os.environ.get("RADIUS_USERNAME")
    password = os.environ.get("RADIUS_PASSWORD")
    if not username or not password:
        raise EnvironmentError("RADIUS_USERNAME and RADIUS_PASSWORD environment variables must be set.")
    page.goto(RADIUS_LOGIN_URL)
    page.fill("#UserName", value=username)
    page.fill("#Password", value=password)
    page.click("#login")
    page.wait_for_load_state("networkidle")


def download_holds_report(page, month_label: str, month: int, year: int) -> Path:
    """Navigate to HoldsReport, search the full target month, read grid data directly.

    Reads from the Kendo grid's dataSource instead of using Export to Excel,
    which returns intermittent 503 errors.
    """
    out_path = INPUT_DIR / "Holds_{}.xlsx".format(month_label)

    last_day = calendar.monthrange(year, month)[1]
    date_from = "{}/1/{}".format(month, year)
    date_to = "{}/{}/{}".format(month, last_day, year)

    page.goto(HOLDS_REPORT_URL)
    page.wait_for_load_state("networkidle")

    # Set date range to cover the full target month
    page.evaluate(
        """([from_, to_]) => {
            $('#ReportStart').val(from_);
            $('#ReportEnd').val(to_);
        }""",
        [date_from, date_to],
    )

    page.click("#btnsearch")
    page.wait_for_load_state("networkidle")

    # Read data directly from the Kendo grid datasource
    records = page.evaluate("""
        () => {
            var grid = $('#gridHoldsReport').data('kendoGrid');
            return grid.dataSource.data().map(function(item) {
                var d = item.toJSON();
                return {
                    'Student Name':   d.StudentName,
                    'Hold End Date':  d.StrHoldEndDt,
                    'Guardian Name':  d.GuardianName,
                    'Guardian Phone': d.GuardianPhone,
                    'Guardian Email': d.GuardianEmail,
                    'Center Name':    d.CenterName,
                };
            });
        }
    """)

    df = pd.DataFrame(records)
    df.to_excel(out_path, index=False)
    return out_path


def download_reports(month_label: str, month: int, year: int) -> dict:
    """Download the Holds Report. Returns {"holds": Path}."""
    INPUT_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        with browser:
            context = browser.new_context()
            with context:
                page = context.new_page()
                _login(page)
                holds_path = download_holds_report(page, month_label, month, year)

    return {"holds": holds_path}
