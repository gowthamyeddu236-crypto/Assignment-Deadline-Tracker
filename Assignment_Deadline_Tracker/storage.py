"""Safe JSON persistence with atomic writes and explicit corruption errors."""
import json
import os
import logging
from pathlib import Path
from typing import Iterable
from .models import Assignment

APP_DIR = Path.home() / ".assignment_deadline_tracker"
DATA_FILE = APP_DIR / "assignments.json"
logger = logging.getLogger(__name__)

class StorageError(Exception):
    """Raised when assignment data cannot safely be read or written."""


def _safe_data_path(path: str | Path | None = None) -> Path:
    # The application controls the filename; callers may choose only a directory.
    if path is None:
        return DATA_FILE
    candidate = Path(path).expanduser()
    if candidate.name != "assignments.json":
        raise StorageError("Data file must be named assignments.json.")
    return candidate.resolve()


def load_assignments(path: str | Path | None = None) -> list[Assignment]:
    target = _safe_data_path(path)
    if not target.exists():
        return []
    try:
        with target.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, list):
            raise StorageError("Data file format is invalid: expected a JSON list.")
        assignments = [Assignment.from_dict(item) for item in payload]
        logger.info("Loaded %d assignments from %s", len(assignments), target)
        return assignments
    except (json.JSONDecodeError, UnicodeDecodeError, OSError, ValueError, TypeError) as exc:
        if isinstance(exc, StorageError):
            raise
        logger.exception("Failed to load assignment data from %s", target)
        raise StorageError(f"Could not safely load {target}: {exc}. Your original file was not changed.") from exc


def save_assignments(assignments: Iterable[Assignment], path: str | Path | None = None) -> None:
    target = _safe_data_path(path)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = target.with_name(target.name + ".tmp")
        with temp.open("w", encoding="utf-8") as handle:
            json.dump([item.to_dict() for item in assignments], handle, indent=2, ensure_ascii=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, target)
        logger.info("Saved %d assignments to %s", len(list(assignments)) if not isinstance(assignments, list) else len(assignments), target)
    except (OSError, TypeError, ValueError) as exc:
        try:
            temp.unlink(missing_ok=True)
        except (OSError, UnboundLocalError):
            pass
        logger.exception("Failed to save assignment data to %s", target)
        raise StorageError(f"Could not save assignments: {exc}") from exc
