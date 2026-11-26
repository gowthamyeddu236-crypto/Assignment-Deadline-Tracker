from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import uuid4

STATUSES = {"Pending", "Completed"}
PRIORITIES = {"Low", "Medium", "High"}

@dataclass
class Assignment:
    title: str
    subject: str
    due_date: str
    priority: str = "Medium"
    status: str = "Pending"
    id: str = ""

    def __post_init__(self) -> None:
        self.id = str(self.id or uuid4())
        self.title = self.title.strip()
        self.subject = self.subject.strip()
        if not self.title or not self.subject:
            raise ValueError("Title and subject cannot be empty.")
        try:
            date.fromisoformat(self.due_date)
        except (TypeError, ValueError) as exc:
            raise ValueError("Due date must be a valid YYYY-MM-DD date.") from exc
        self.priority = self.priority.title()
        self.status = self.status.title()
        if self.priority not in PRIORITIES:
            raise ValueError("Priority must be Low, Medium, or High.")
        if self.status not in STATUSES:
            raise ValueError("Status must be Pending or Completed.")

    @property
    def is_overdue(self) -> bool:
        return self.status == "Pending" and date.fromisoformat(self.due_date) < date.today()

    @property
    def days_remaining(self) -> int:
        return (date.fromisoformat(self.due_date) - date.today()).days

    def mark_completed(self) -> None:
        self.status = "Completed"

    def to_dict(self) -> dict[str, str]:
        return {"id": self.id, "title": self.title, "subject": self.subject, "due_date": self.due_date,
                "priority": self.priority, "status": self.status}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Assignment":
        required = {"title", "subject", "due_date"}
        if not isinstance(data, dict) or not required.issubset(data):
            raise ValueError("Assignment record is missing required fields.")
        return cls(data["title"], data["subject"], data["due_date"],
                   data.get("priority", "Medium"), data.get("status", "Pending"), data.get("id", ""))

    def __str__(self) -> str:
        flag = "OVERDUE" if self.is_overdue else self.status.upper()
        return f"[{flag}] {self.title} | {self.subject} | Due {self.due_date} | {self.priority}"
