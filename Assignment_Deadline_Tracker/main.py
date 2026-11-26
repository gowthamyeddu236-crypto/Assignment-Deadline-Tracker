"""Command-line interface for Assignment Deadline Tracker."""
import logging
from .service import AssignmentService
from .storage import StorageError
from .analytics import create_dashboard

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def show(items, start=0):
    if not items:
        print("No matching assignments.")
        return
    for i, item in enumerate(items, start + 1):
        print(f"{i}. ID: {item.id} | {item}")


def main():
    try:
        service = AssignmentService()
    except StorageError as exc:
        print(f"Data could not be loaded safely: {exc}")
        return
    while True:
        print("\n=== Assignment Deadline Tracker ===")
        print("1. View assignments  2. Add  3. Mark completed  4. Search/filter")
        print("5. Analytics summary  6. Export chart  7. Delete  8. Exit")
        choice = input("Choose (1-8): ").strip()
        try:
            if choice == "1":
                page = 1
                while True:
                    items, page, pages = service.page(page=page, page_size=10)
                    print(f"\nPage {page}/{pages}")
                    show(items, (page - 1) * 10)
                    if pages == 1: break
                    action = input("N=next, P=previous, Enter=back: ").strip().lower()
                    if action == "n": page = min(pages, page + 1)
                    elif action == "p": page = max(1, page - 1)
                    else: break
            elif choice == "2":
                service.add(input("Title: "), input("Subject: "), input("Due date (YYYY-MM-DD): "),
                            input("Priority [Low/Medium/High, default Medium]: ").strip() or "Medium")
                print("Assignment added.")
            elif choice == "3":
                show(service.assignments)
                if service.assignments:
                    service.complete(input("Assignment UUID: ").strip())
                    print("Marked completed.")
            elif choice == "4":
                results = service.search(input("Search title/subject (blank=all): "),
                    input("Status [All/Pending/Completed]: ").strip().title() or "All",
                    input("Priority [All/Low/Medium/High]: ").strip().title() or "All")
                show(results)
            elif choice == "5":
                s = service.analytics()
                print("\n--- Summary ---")
                for key in ("total", "pending", "completed", "overdue", "due_next_7_days", "completion_rate"):
                    print(f"{key.replace('_', ' ').title()}: {s[key]}")
                print("\nOverdue assignments:"); show(s["overdue_items"])
                print("\nDue in next 7 days:"); show(s["upcoming_items"])
            elif choice == "6":
                print(f"Chart saved to: {create_dashboard(service)}")
            elif choice == "7":
                show(service.assignments)
                if service.assignments:
                    service.delete(input("Assignment UUID: ").strip())
                    print("Assignment deleted.")
            elif choice == "8":
                print("Goodbye!"); break
            else:
                print("Choose a number from 1 to 8.")
        except (ValueError, IndexError, StorageError, RuntimeError) as exc:
            logger.warning("CLI action failed: %s", exc)
            print(f"Unable to complete action: {exc}")

if __name__ == "__main__":
    main()
