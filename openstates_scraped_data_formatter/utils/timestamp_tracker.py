from pathlib import Path
from datetime import datetime
import json

LATEST_TIMESTAMP_PATH = (
    Path(__file__).resolve().parents[2] / "data_output/latest_timestamp_seen.txt"
)

latest_timestamps = {
    "bills": None,
    "vote_events": None,
    "events": None,
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
