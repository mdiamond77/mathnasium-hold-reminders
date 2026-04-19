import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import CENTERS, CC_RECIPIENT


def _table_rows(rows: list[dict], cols: list[str]) -> str:
    if not rows:
        return "<tr><td colspan='{}' style='color:#888;font-style:italic;'>None this month.</td></tr>".format(len(cols))
    return "".join(
        "<tr>" + "".join(
            "<td style='padding:6px 12px;border:1px solid #ddd;'>{}</td>".format(row.get(c, ""))
            for c in cols
        ) + "</tr>"
        for row in rows
    )


def _table(headers: list[str], rows: list[dict], cols: list[str]) -> str:
    header_html = "".join(
        "<th style='padding:6px 12px;border:1px solid #ddd;background:#f5f5f5;text-align:left;'>{}</th>".format(h)
        for h in headers
    )
    return (
        "<table style='border-collapse:collapse;font-family:Arial,sans-serif;"
        "font-size:14px;margin-bottom:8px;'>"
        "<tr>{}</tr>"
        "{}"
        "</table>"
    ).format(header_html, _table_rows(rows, cols))


def build_html(center_name: str, month_label: str, holds: list[dict]) -> str:
    """Build the full HTML email body for one center."""
    display_rows = [
        {
            "Student": h["name"],
            "Hold End Date": h["hold_end_date"],
            "Guardian": h["guardian_name"],
            "Phone": h["guardian_phone"],
            "Email": h["guardian_email"],
        }
        for h in holds
    ]
    table_html = _table(
        ["Student", "Hold End Date", "Guardian", "Phone", "Email"],
        display_rows,
        ["Student", "Hold End Date", "Guardian", "Phone", "Email"],
    )
    divider = "<hr style='border:none;border-top:2px solid #ccc;margin:24px 0;'>"

    return (
        "<html><body style='font-family:Arial,sans-serif;font-size:14px;"
        "max-width:700px;margin:0 auto;padding:20px;'>"
        "<p>Hi {center} Team,</p>"
        "<p>The following students are scheduled to come off hold this month and return "
        "to billing for the next cycle. Please confirm each one is still correct before "
        "the end of the month.</p>"
        "{divider}"
        "{table}"
        "{divider}"
        "<p><strong>Reminder:</strong> Please also add any students to next month's holds "
        "if they have notified you that they are going on hold.</p>"
        "<p style='color:#999;font-size:12px;'><em>This email sends automatically on the "
        "last Monday, Tuesday, and Thursday of each month. "
        "Questions? Contact matt.diamond@mathnasium.com.</em></p>"
        "</body></html>"
    ).format(center=center_name, divider=divider, table=table_html)


def send_email(center_name: str, month_label: str, html: str) -> None:
    """Send the HTML email for one center via Gmail SMTP."""
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    recipient = CENTERS[center_name]["recipient"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Hold Reminders \u2014 {} \u2014 {}".format(center_name, month_label)
    msg["From"] = smtp_user
    msg["To"] = recipient
    msg["Cc"] = CC_RECIPIENT

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, [recipient, CC_RECIPIENT], msg.as_string())


def deliver(center_data: dict, month_label: str) -> None:
    """Send one email per center. Centers with no holds are skipped silently."""
    for center_name, holds in center_data.items():
        if not holds:
            print("No holds for {} this month, skipping.".format(center_name))
            continue
        html = build_html(center_name, month_label, holds)
        send_email(center_name, month_label, html)
        print("Sent email for {}".format(center_name))
