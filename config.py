import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"

RADIUS_LOGIN_URL = "https://radius.mathnasium.com"
HOLDS_REPORT_URL = "https://radius.mathnasium.com/Holds/HoldsReport"

CENTERS = {
    "Englewood": {"radius_id": "2428", "recipient": "englewood@mathnasium.com"},
    "Teaneck":   {"radius_id": "2871", "recipient": "teaneck@mathnasium.com"},
}
CC_RECIPIENT = "matt.diamond@mathnasium.com"

# Column names verified from real Radius Holds Report export (4/18/2026)
COL_STUDENT_NAME   = "Student Name"
COL_HOLD_END_DATE  = "Hold End Date"
COL_GUARDIAN_NAME  = "Guardian Name"
COL_GUARDIAN_PHONE = "Guardian Phone"
COL_GUARDIAN_EMAIL = "Guardian Email"
COL_CENTER         = "Center Name"
