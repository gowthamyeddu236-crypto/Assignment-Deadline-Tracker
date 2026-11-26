"""Shared business logic used by both command-line and desktop interfaces."""
from collections import Counter
import logging
from datetime import date
from .models import Assignment
from .storage import load_assignments, save_assignments
from .validators import validate_text, validate_date, validate_priority

logger = logging.getLogger(__name__)

class AssignmentService:
    def __init__(self, data_path=None):
        self.data_path = data_path
        self.assignments = load_assignments(data_path)
        logger.info("Loaded %d assignments", len(self.assignments))

    def _save(self):
        save_assignments(self.assignments, self.data_path)
        logger.debug("Persisted %d assignments", len(self.assignments))

    def add(self, title, subject, due_date, priority="Medium") -> Assignment:
        title = validate_text(title, "Title")
        subject = validate_text(subject, "Subject")
        if not validate_date(due_date):
            raise ValueError("Enter a real date in YYYY-MM-DD format.")
        if not validate_priority(priority):
            raise ValueError("Priority must be Low, Medium, or High.")
        item = Assignment(title, subject, due_date, priority)
        self.assignments.append(item)
        self._save()
        logger.info("Assignment created: id=%s", item.id)
        return item

    def complete(self, index: int | str) -> Assignment:
        item = self._get(index)
        item.mark_completed()
        self._save()
        logger.info("Assignment completed: id=%s", item.id)
        return item

    def delete(self, index: int | str) -> Assignment:
        item = self._get(index)
        self.assignments.remove(item)
        self._save()
        logger.info("Assignment deleted: id=%s", item.id)
        return item

    def update(self, index: int | str, **changes) -> Assignment:
        old = self._get(index)
        updated = Assignment(changes.get("title", old.title), changes.get("subject", old.subject),
                             changes.get("due_date", old.due_date), changes.get("priority", old.priority),
                             changes.get("status", old.status))
        updated.id = old.id
        self.assignments[self.assignments.index(old)] = updated
        self._save()
        return updated

    def _get(self, identifier):
        # UUID is the canonical identifier. Integer positions remain supported
        # for compatibility with existing integrations and older tests.
        if isinstance(identifier, int):
            if identifier < 0 or identifier >= len(self.assignments):
                raise IndexError("Assignment number is out of range.")
            return self.assignments[identifier]
        for item in self.assignments:
            if item.id == str(identifier):
                return item
        raise IndexError("Assignment ID was not found.")

    def get_by_id(self, assignment_id: str) -> Assignment:
        """Return an assignment by its stable UUID."""
        return self._get(assignment_id)

    def search(self, query="", status="All", priority="All", subject="All"):
        q = query.casefold().strip()
        return [a for a in self.assignments
                if (not q or q in a.title.casefold() or q in a.subject.casefold())
                and (status == "All" or a.status == status)
                and (priority == "All" or a.priority == priority)
                and (subject == "All" or a.subject.casefold() == subject.casefold())]

    def analytics(self):
        today = date.today()
        pending = [a for a in self.assignments if a.status == "Pending"]
        completed = [a for a in self.assignments if a.status == "Completed"]
        overdue = [a for a in pending if a.is_overdue]
        upcoming = [a for a in pending if 0 <= a.days_remaining <= 7]
        return {"total": len(self.assignments), "pending": len(pending), "completed": len(completed),
                "overdue": len(overdue), "due_next_7_days": len(upcoming),
                "completion_rate": round(len(completed) / len(self.assignments) * 100, 1) if self.assignments else 0.0,
                "priority_counts": dict(Counter(a.priority for a in pending)),
                "subject_counts": dict(Counter(a.subject for a in self.assignments)),
                "overdue_items": overdue, "upcoming_items": sorted(upcoming, key=lambda a: a.due_date)}

    def page(self, items=None, page=1, page_size=10):
        items = self.assignments if items is None else items
        if page_size < 1: raise ValueError("Page size must be positive.")
        pages = max(1, (len(items) + page_size - 1) // page_size)
        page = min(max(1, page), pages)
        start = (page - 1) * page_size
        return items[start:start + page_size], page, pages
