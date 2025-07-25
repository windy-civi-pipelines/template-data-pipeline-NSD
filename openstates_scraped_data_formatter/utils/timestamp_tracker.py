from pathlib import Path
from datetime import datetime
import json

LATEST_TIMESTAMP_PATH = (
    Path(__file__).resolve().parents[2] / "data_output/latest_timestamp_seen.txt"
)

{
    "bills": "19000101T000000",
    "vote_events": "19000101T000000",
    "events": "19000101T000000",
}


def read_latest_timestamp(data_type):
    try:
        with open(LATEST_TIMESTAMP_PATH, "r", encoding="utf-8") as f:
            all_timestamps = json.load(f)
            return all_timestamps.get(data_type)
    except FileNotFoundError:
        return "1900-01-01T00:00:00"


def to_dt_obj(ts_str):
    try:
        ts_str = ts_str.rstrip("Z")
        return datetime.strptime(ts_str, "%Y%m%dT%H%M%S")
    except Exception:
        return None


def update_latest_timestamp(category, current_dt, existing_dt):
    if current_dt and (not existing_dt or current_dt > existing_dt):
        latest_timestamps[category] = current_dt
        print(f"🕓 Updating {category} latest timestamp to {current_dt}")
        return current_dt
    return existing_dt


def is_newer_than_latest(content: dict, latest_timestamp_dt: datetime) -> bool:
    """
    Checks if the given content has a timestamp newer than the latest seen.

    Looks in typical timestamp fields like "start_date" or "date".
    Defaults to True if no timestamp can be found or parsed.

    Args:
        content (dict): The JSON-loaded content of the file.
        latest_timestamp_dt (datetime): Latest datetime seen for this category.

    Returns:
        bool: True if content is newer (or undated), False if outdated.
    """
    raw_ts = content.get("start_date") or content.get("date")
    if not raw_ts:
        return True  # Allow through if no date field

    try:
        # Strip timezone Z if present
        raw_ts = raw_ts.rstrip("Z")
        current_dt = datetime.strptime(raw_ts, "%Y-%m-%dT%H:%M:%S")
        return current_dt > latest_timestamp_dt
    except Exception:
        return True  # If parsing fails, allow through


def write_latest_timestamp_file():
    try:
        output = {}
        for k, dt in latest_timestamps.items():
            if dt:
                output[k] = dt.strftime("%Y-%m-%dT%H:%M:%S")

        if not output:
            print("⚠️ No timestamps to write.")
            return

        LATEST_TIMESTAMP_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LATEST_TIMESTAMP_PATH, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        print(f"📝 Updated latest timestamp path: {LATEST_TIMESTAMP_PATH}")
        print("📄 File contents:")
        print(json.dumps(output, indent=2))

    except Exception as e:
        print(f"❌ Failed to write latest timestamp: {e}")
