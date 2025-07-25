import os
import json
from utils.file_utils import record_error_file
import os
import json
from utils.file_utils import record_error_file
from utils.timestamp_tracker import (
    is_newer_than_latest,
)


def load_json_files(
    input_folder, EVENT_ARCHIVE_FOLDER, ERROR_FOLDER, latest_timestamps_dt
):
    bills_ts = latest_timestamps_dt["bills"]
    vote_events_ts = latest_timestamps_dt["vote_events"]
    events_ts = latest_timestamps_dt["events"]

    all_data = []
    for filename in os.listdir(input_folder):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(input_folder, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

                # Determine type for timestamp comparison
                if filename.startswith("bill"):
                    if not is_newer_than_latest(data, bills_ts, "bill"):
                        continue
                elif filename.startswith("vote_event"):
                    if not is_newer_than_latest(data, vote_events_ts, "vote_event"):
                        continue
                elif filename.startswith("event"):
                    if not is_newer_than_latest(data, events_ts, "event"):
                        continue

                all_data.append((filename, data))

                # Archive event_*.json files
                if filename.startswith("event_"):
                    EVENT_ARCHIVE_FOLDER.mkdir(parents=True, exist_ok=True)
                    missing_event_file = ERROR_FOLDER / "missing_session" / filename
                    if missing_event_file.exists():
                        missing_event_file.unlink()

                    archive_path = EVENT_ARCHIVE_FOLDER / filename
                    with open(archive_path, "w", encoding="utf-8") as archive_f:
                        json.dump(data, archive_f, indent=2)

        except json.JSONDecodeError:
            print(f"❌ Skipping {filename}: could not parse JSON")
            with open(filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()
            record_error_file(
                ERROR_FOLDER,
                "invalid_json",
                filename,
                {"error": "Could not parse JSON", "raw": raw_text},
                original_filename=filename,
            )

    return all_data
