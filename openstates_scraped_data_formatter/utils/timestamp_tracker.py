from pathlib import Path
from datetime import datetime
import json
from utils.file_utils import format_timestamp

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
    if isinstance(ts_str, datetime):
        return ts_str
    try:
        ts_str = ts_str.rstrip("Z")
        if "-" in ts_str:
            return datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")
        else:
            return datetime.strptime(ts_str, "%Y%m%dT%H%M%S")
    except Exception as e:
        print(f"❌ Failed to parse timestamp: {ts_str} ({e})")
        return None


def update_latest_timestamp(category, current_dt, existing_dt):
    if not current_dt:
        return existing_dt

    if not existing_dt or current_dt > existing_dt:
        latest_timestamps[category] = current_dt
        print(f"🕓 Updating {category} latest timestamp to {current_dt}")
        print(f"📄 File contents: {latest_timestamps}")
        return current_dt

    return existing_dt


def extract_timestamp(content, category: str) -> str | None:
    try:
        if category == "bills":
            actions = content.get("actions", [])
            dates = [a.get("date") for a in actions if a.get("date")]
            return format_timestamp(sorted(dates)[-1]) if dates else None

        elif category == "events":
            return format_timestamp(content.get("start_date"))

        elif category == "vote_events":
            return format_timestamp(content.get("start_date"))

        else:
            return None
    except Exception as e:
        print(f"❌ Failed to extract timestamp for {category}: {e}")
        return None


def is_newer_than_latest(content, latest_timestamp_dt: datetime, category: str) -> bool:
    raw_ts = extract_timestamp(content, category)
    print(
        f"💬 Extracted raw_ts for {category}: {raw_ts} vs latest: {latest_timestamp_dt}"
    )

    if not raw_ts:
        return True

    try:
        current_dt = to_dt_obj(raw_ts)
        return current_dt > latest_timestamp_dt
    except Exception as e:
        print(f"❌ Failed to parse {raw_ts}: {e}")
        return True


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
