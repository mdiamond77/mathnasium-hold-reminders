import os
import tempfile
from pathlib import Path

import pandas as pd
from playwright.sync_api import sync_playwright

from config import INPUT_DIR, RADIUS_LOGIN_URL, HOLDS_REPORT_URL, CENTERS


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


def _select_center(page, center_id: str) -> None:
    """Select a single center in the Holds Report DropDownList."""
    page.evaluate(
        """(id) => {
            const dd = $('#centersDropDownList').data('kendoDropDownList');
            dd.value(id);
            dd.trigger('change');
        }""",
        center_id,
    )


def _download_for_center(page, center_id: str) -> Path:
    """Download the Holds Report for one center; returns a temp file path."""
    page.goto(HOLDS_REPORT_URL)
    page.wait_for_load_state("networkidle")

    _select_center(page, center_id)

    page.click("#btnsearch")
    page.wait_for_load_state("networkidle")

    tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    tmp.close()
    tmp_path = Path(tmp.name)

    with page.expect_download() as dl:
        page.click("#btnExport")
    dl.value.save_as(tmp_path)

    return tmp_path


def download_holds_report(page, month_label: str) -> Path:
    """Download Holds Report for each center and combine into one Excel file."""
    out_path = INPUT_DIR / "Holds_{}.xlsx".format(month_label)

    frames = []
    for center_cfg in CENTERS.values():
        tmp_path = _download_for_center(page, center_cfg["radius_id"])
        try:
            df = pd.read_excel(tmp_path)
            frames.append(df)
        finally:
            tmp_path.unlink(missing_ok=True)

    combined = pd.concat(frames, ignore_index=True)
    combined.to_excel(out_path, index=False)

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
