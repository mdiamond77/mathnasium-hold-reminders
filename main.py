import argparse
import traceback
from calendar import monthrange
from datetime import date

from download import download_reports
from process import process
from deliver import deliver
from run_log import write_log


def is_last_week_of_month(today: date = None) -> bool:
    """Return True if today is within the last 7 days of the month."""
    if today is None:
        today = date.today()
    last_day = monthrange(today.year, today.month)[1]
    return (last_day - today.day) < 7


def get_month_label(month_str: str) -> str:
    """Convert 'YYYY-MM' to 'Month YYYY', e.g. '2026-04' -> 'April 2026'."""
    year, month = month_str.split("-")
    month_name = date(int(year), int(month), 1).strftime("%B")
    return "{} {}".format(month_name, year)


def main():
    parser = argparse.ArgumentParser(description="Run Hold Reminder Emails automation.")
    parser.add_argument(
        "--trigger",
        default="auto",
        choices=["auto", "manual"],
        help="How this run was triggered (default: auto)",
    )
    parser.add_argument(
        "--month",
        default=date.today().strftime("%Y-%m"),
        help="Month to process in YYYY-MM format (default: current month)",
    )
    args = parser.parse_args()

    month_str = args.month
    month_label = get_month_label(month_str)
    year = int(month_str.split("-")[0])
    month_num = int(month_str.split("-")[1])

    if args.trigger == "auto" and not is_last_week_of_month():
        print("Not in last 7 days of month — skipping.")
        return

    print("Running Hold Reminders for {}".format(month_label))

    try:
        print("Downloading holds report...")
        paths = download_reports(month_label)

        print("Processing data...")
        center_data = process(paths["holds"], month=month_num, year=year)

        print("Sending emails...")
        deliver(center_data, month_label)

        write_log(month_str, success=True, trigger=args.trigger)
        print("Done.")

    except Exception as e:
        error_msg = traceback.format_exc()
        print("ERROR: {}".format(e))
        print(error_msg)
        write_log(month_str, success=False, trigger=args.trigger, error=error_msg)
        raise


if __name__ == "__main__":
    main()
