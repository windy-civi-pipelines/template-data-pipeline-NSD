from pathlib import Path
from datetime import datetime
import json

LATEST_TIMESTAMP_PATH = (
    Path(__file__).resolve().parents[2] / "data_output/latest_timestamp_seen.txt"
)

latest_timestamps = {
    "bills": "19000101T000000",
    "vote_events": "19000101T000000",
    "events": "19000101T000000",
}


def read_all_latest_timestamps():
    try:
        with open(LATEST_TIMESTAMP_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
            return {k: to_dt_obj(v) for k, v in raw.items() if v}
    except Exception:
        print("⚠️ No timestamp file found or invalid JSON. Using defaults.")
        return {
            "bills": datetime(1900, 1, 1),
            "vote_events": datetime(1900, 1, 1),
            "events": datetime(1900, 1, 1),
        }


def to_dt_obj(ts_str):
    try:
        ts_str = ts_str.rstrip("Z")
        return datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")
    except Exception:
        print(f"❌ Failed to parse timestamp: {ts_str}")
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


from .timestamp_tracker import to_dt_obj  # or make sure it's imported


def write_latest_timestamp_file():
    try:
        output = {}
        for k, dt in latest_timestamps.items():
            dt_obj = to_dt_obj(dt) if isinstance(dt, str) else dt
            if dt_obj:
                output[k] = dt_obj.strftime("%Y-%m-%dT%H:%M:%S")

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
