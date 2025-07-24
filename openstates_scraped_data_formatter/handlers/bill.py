from pathlib import Path
import json
import re
from urllib import request
from urllib.parse import urlparse
from utils.file_utils import format_timestamp, record_error_file, write_action_logs
from utils.download_pdf import download_bill_pdf
from utils import timestamp_tracker
from utils.timestamp_tracker import (
    read_latest_timestamp,
    to_dt_obj,
)

LATEST_TIMESTAMP = to_dt_obj(read_latest_timestamp())
print(f"Current latest timestamp: {LATEST_TIMESTAMP}")


def handle_bill(
    STATE_ABBR,
    content,
    session_name,
    date_folder,
    DATA_PROCESSED_FOLDER,
    DATA_NOT_PROCESSED_FOLDER,
    filename,
):
    """
    Handles a bill JSON file by saving:

    1. A full snapshot of the bill in logs/ using the earliest action date
    2. One separate JSON file per action in logs/, each timestamped and slugified
    3. A files/ directory, with any linked PDFs downloaded (optional)

    Skips and logs errors if required fields (e.g. identifier) are missing.

    Returns:
        bool: True if saved successfully, False if skipped due to missing identifier.
    """

    # Optional: Download linked PDF files (⚠️ very slow).
    # Default is OFF to preserve performance.
    DOWNLOAD_PDFS = False
    global LATEST_TIMESTAMP

    bill_identifier = content.get("identifier")
    if not bill_identifier:
        print("⚠️ Warning: Bill missing identifier")
        record_error_file(
            DATA_NOT_PROCESSED_FOLDER,
            "from_handle_bill_missing_identifier",
            filename,
            content,
            original_filename=filename,
        )
        return False

    save_path = Path(DATA_PROCESSED_FOLDER).joinpath(
        f"country:us",
        f"state:{STATE_ABBR}",
        "sessions",
        "ocd-session",
        f"country:us",
        f"state:{STATE_ABBR}",
        date_folder,
        session_name,
        "bills",
        bill_identifier,
    )
    (save_path / "logs").mkdir(parents=True, exist_ok=True)
    (save_path / "files").mkdir(parents=True, exist_ok=True)

    actions = content.get("actions", [])
    if actions:
        dates = [a.get("date") for a in actions if a.get("date")]
        timestamp = format_timestamp(sorted(dates)[0]) if dates else None
        if timestamp and timestamp != "unknown":
            current_dt = to_dt_obj(timestamp)
            if current_dt and (
                not timestamp_tracker.LATEST_TIMESTAMP
                or current_dt > timestamp_tracker.LATEST_TIMESTAMP
            ):
                timestamp_tracker.LATEST_TIMESTAMP = current_dt
                print(f"Updating latest timestamp to {LATEST_TIMESTAMP}")
    else:
        timestamp = None

    if not timestamp:
        print(f"⚠️ Warning: Bill {bill_identifier} missing action dates")
        timestamp = "unknown"

    # Save entire bill
    full_filename = f"{timestamp}_entire_bill.json"
    output_file = save_path.joinpath("logs", full_filename)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2)

    # Save each action as a separate file
    if actions:
        write_action_logs(actions, bill_identifier, save_path / "logs")

    # Download associated bill PDFs: if enabled
    if DOWNLOAD_PDFS:
        download_bill_pdf(content, save_path, bill_identifier)

    return True
