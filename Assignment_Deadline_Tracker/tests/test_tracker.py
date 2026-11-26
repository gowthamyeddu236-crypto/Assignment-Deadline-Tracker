import json
import pytest
from datetime import date, timedelta
from assignment_deadline_tracker.models import Assignment
from assignment_deadline_tracker.service import AssignmentService
from assignment_deadline_tracker.storage import load_assignments, save_assignments, StorageError
from assignment_deadline_tracker.validators import validate_date, validate_priority


def test_validation():
    assert validate_date("2026-12-01")
    assert not validate_date("2026-02-30")
    assert validate_priority("high")
    assert not validate_priority("urgent")


def test_add_search_and_persistence(tmp_path):
    path = tmp_path / "assignments.json"
    service = AssignmentService(path)
    service.add("Maths project", "Mathematics", "2026-12-01", "High")
    assert len(service.search("math")) == 1
    assert load_assignments(path)[0].title == "Maths project"


def test_analytics_and_completion(tmp_path):
    path = tmp_path / "assignments.json"
    service = AssignmentService(path)
    service.add("Old task", "Physics", (date.today() - timedelta(days=1)).isoformat())
    service.add("Future task", "Maths", (date.today() + timedelta(days=2)).isoformat(), "High")
    assert service.analytics()["overdue"] == 1
    service.complete(0)
    assert service.analytics()["completed"] == 1
    assert service.analytics()["overdue"] == 0


def test_pagination(tmp_path):
    service = AssignmentService(tmp_path / "assignments.json")
    for n in range(12): service.add(f"Task {n}", "CS", "2026-12-20")
    items, page, pages = service.page(page=2, page_size=10)
    assert (len(items), page, pages) == (2, 2, 2)


def test_corrupt_json_is_not_silently_erased(tmp_path):
    path = tmp_path / "assignments.json"
    path.write_text("{broken", encoding="utf-8")
    with pytest.raises(StorageError): load_assignments(path)
    assert path.read_text(encoding="utf-8") == "{broken"


def test_path_filename_is_restricted(tmp_path):
    with pytest.raises(StorageError): load_assignments(tmp_path / "other.json")


def test_invalid_record_rejected():
    with pytest.raises(ValueError): Assignment.from_dict({"title": "x"})



def test_assignments_receive_unique_stable_uuids(tmp_path):
    path = tmp_path / "assignments.json"
    service = AssignmentService(path)
    first = service.add("Task A", "Maths", "2026-12-01")
    second = service.add("Task B", "Physics", "2026-12-02")
    assert first.id != second.id
    assert len(first.id) == 36
    reloaded = AssignmentService(path)
    assert reloaded.get_by_id(first.id).title == "Task A"
    reloaded.complete(first.id)
    assert AssignmentService(path).get_by_id(first.id).status == "Completed"


def test_legacy_records_get_uuid_on_load(tmp_path):
    path = tmp_path / "assignments.json"
    path.write_text(json.dumps([{
        "title": "Legacy task", "subject": "History", "due_date": "2026-12-01"
    }]), encoding="utf-8")
    loaded = load_assignments(path)
    assert loaded[0].id
    save_assignments(loaded, path)
    assert json.loads(path.read_text(encoding="utf-8"))[0]["id"] == loaded[0].id



def test_update_preserves_uuid(tmp_path):
    service = AssignmentService(tmp_path / "assignments.json")
    created = service.add("Original", "Computing", "2026-12-10")
    updated = service.update(created.id, title="Updated")
    assert updated.id == created.id
    assert AssignmentService(tmp_path / "assignments.json").get_by_id(created.id).title == "Updated"
