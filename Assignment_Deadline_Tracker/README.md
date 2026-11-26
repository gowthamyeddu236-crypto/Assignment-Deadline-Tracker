# Assignment Deadline Tracker 2.0

A Python assignment tracker with both a terminal interface and a Tkinter desktop interface. Both interfaces use the same `AssignmentService` business logic. Each record receives a UUID that remains stable across reloads; legacy records without an ID receive one when loaded and it is persisted on the next save.

## Features
- Add, update (service API), complete and delete assignments
- Search by title or subject; filter by status and priority
- Detect overdue work and assignments due in the next seven days
- Summary analytics and Matplotlib dashboard export
- UUID-based stable record IDs (including automatic migration of older JSON records)
- JSON persistence with atomic writes and explicit corruption errors (never silently replaces damaged data)
- Structured application logging with Python's standard `logging` module
- GitHub Actions CI for automated pytest runs on Python 3.10, 3.11 and 3.12
- Input validation, fixed data filename, paginated CLI/GUI lists
- Automated pytest tests

## Requirements
- Python 3.10+
- Tkinter (usually included with standard Python installations; Linux may require `python3-tk`)
- Matplotlib for chart export; pytest for tests

Install optional dependencies:
```bash
python -m pip install -r requirements.txt
```

## Run
Run commands from the directory containing this README:
```bash
python -m assignment_deadline_tracker.main   # terminal interface
python -m assignment_deadline_tracker.gui    # desktop interface
```

## Data location
Data is stored at `~/.assignment_deadline_tracker/assignments.json` (the current user's home directory). The application does not overwrite malformed JSON; it reports the problem so the original data can be recovered.

## Logging

The CLI and GUI configure readable timestamped logs. The application modules use standard Python logging; set `logging` levels in your launcher to control verbosity. Logs are emitted to the console and do not contain assignment descriptions.

## Continuous integration

A GitHub Actions workflow at `.github/workflows/ci.yml` runs the test suite on pushes, pull requests and manual dispatches across Python 3.10–3.12.

## Tests
From the directory containing this README:
```bash
python -m pytest -q
```

## Export charts
Choose **Export chart** in the GUI analytics prompt, or select option 6 in the CLI. The PNG is written to `reports/assignment_dashboard.png` under the current working directory.
