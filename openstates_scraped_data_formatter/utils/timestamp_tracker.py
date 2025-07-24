from pathlib import Path
from datetime import datetime
import json

LATEST_TIMESTAMP_PATH = (
    Path(__file__).resolve().parents[2] / "data_output/latest_timestamp_seen.txt"
)


def read_latest_timestamp():
    try:
        return LATEST_TIMESTAMP_PATH.read_text().strip()
    except FileNotFoundError:
        return None


def to_dt_obj(ts_str):
    try:
        ts_str = ts_str.rstrip("Z")
        return datetime.strptime(ts_str, "%Y%m%dT%H%M%S")
    except Exception:
        return None


def write_latest_timestamp(timestamp):
    try:
        Path(LATEST_TIMESTAMP_PATH).parent.mkdir(parents=True, exist_ok=True)
        Path(LATEST_TIMESTAMP_PATH).write_text(timestamp)
        print(f"📝 Updated latest timestamp path: {LATEST_TIMESTAMP_PATH}")
        print(f"📝 Updated latest timestamp file: {timestamp}")

        # ✅ Print file contents to confirm
        print("📄 File contents:")
        print(Path(LATEST_TIMESTAMP_PATH).read_text())

    except Exception as e:
        print(f"❌ Failed to write latest timestamp: {e}")


LATEST_TIMESTAMP = to_dt_obj(read_latest_timestamp())
