import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

from config import INPUT_DIR, RADIUS_LOGIN_URL, HOLDS_REPORT_URL, CENTERS

CENTER_IDS = [c["radius_id"] for c in CENTERS.values()]


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


def _select_all_centers(page) -> None:
    """Select both Englewood and Teaneck in the center Kendo MultiSelect."""
    page.evaluate(
        """(ids) => {
            const ms = $('#AllCenterListMultiSelect').data('kendoMultiSelect');
            ms.value(ids);
            ms.trigger('change');
        }""",
        json.dumps(CENTER_IDS),
    )


def download_holds_report(page, month_label: str) -> Path:
    """Navigate to HoldsReport, select both centers, export to Excel."""
    out_path = INPUT_DIR / "Holds_{}.xlsx".format(month_label)

    page.goto(HOLDS_REPORT_URL)
    page.wait_for_load_state("networkidle")

    _select_all_centers(page)

    page.click("#btnsearch")
    page.wait_for_load_state("networkidle")

    with page.expect_download() as dl:
        page.click("#btnExport")
    dl.value.save_as(out_path)

    return out_path


def download_reports(month_label: str) -> dict:
    """Download the Holds Report. Returns {"holds": Path}."""
    INPUT_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        with browser:
            context = browser.new_context(accept_downloads=True)
            with context:
                page = context.new_page()
                _login(page)
                holds_path = download_holds_report(page, month_label)

    return {"holds": holds_path}
