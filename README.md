# STATE-windy-civi-data-pipeline

This repository provides a self-contained GitHub Actions workflow to:

1. 🧹 **Scrape** data for a single U.S. state from the OpenStates project
2. 🧼 **Sanitize** it (removing `_id` and `scraped_at` fields for deterministic output)
3. 🧠 **Format** it into a blockchain-style, versioned data structure
4. 📂 **Commit** the formatted output to this repo nightly (or manually)

---

## 🔧 Setup Instructions

1. **Create a new repo** using this one as a template (via GitHub's "Use this template" button).
2. **Rename your repo** using the convention: `STATE-windy-civi-data-pipeline`, replacing `STATE` with the 2-letter abbreviation (e.g. `il`, `tx`, `wi`).
3. In `.github/workflows/update-data.yml`, update the `STATE` value under `env:` to match your state.
4. Enable GitHub Actions in your repo.

Once set up, the pipeline will run:

- ♻️ **Every night at 1am UTC**, and
- 🧑‍💻 **Any time you manually trigger it from the GitHub UI**

---

## 📁 Folder Structure

```
STATE-windy-civi-data-pipeline/
├── .github/
│   └── workflows/
│       └── update-data.yml         # GitHub Actions pipeline
├── formatter/
│   └── openstates_scraped_data_formatter/   # Formatter for blockchain-style output
├── bill_session_mapping/          # JSON mapping of bill IDs to sessions
├── sessions/                      # Session metadata (e.g. dates, labels)
├── data_output/                   # Formatter output files
│   ├── data_processed/            # Clean structured output by session and bill
│   ├── data_not_processed/        # Items that could not be parsed or routed
│   └── event_archive/             # Raw extracted events saved for post-processing
├── Pipfile, Pipfile.lock          # Formatter dependencies
├── README.md                      # This file
```

---

## 📦 Output Format

Formatted data is saved to `data_output/data_processed/`, organized by session and bill. Each folder includes:

- `logs/`: timestamped JSONs for bill actions, events, and votes
- `files/`: placeholder for source documents (if enabled)
- `snapshot-<timestamp>.tgz`: compressed archive of the full structured output (used in past workflows but currently not saved)

Additional folders:

- `data_not_processed/`: Items that could not be fully parsed or matched (e.g. missing session info)
- `event_archive/`: Extracted events temporarily stored for linking to bill actions

---

## 🔁 Notes on Workflow Behavior

- The `data_output/`, `bill_session_mapping/`, and `sessions/` folders persist in the repo after each run
- GitHub Actions writes directly to those folders using `rsync`
- No folders are auto-deleted; only overwritten if files change
- Session mappings and new session logs are automatically updated

---

## 💬 Questions or Contributions?

This is part of the [Windy Civi](https://github.com/windy-civi) project. If you're working on a new state, want to suggest improvements, or need help, feel free to open an issue or join our Slack!
