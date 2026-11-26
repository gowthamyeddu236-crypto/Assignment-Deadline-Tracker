"""Tkinter desktop interface. Business rules are shared through AssignmentService."""
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from .service import AssignmentService
from .storage import StorageError
from .analytics import create_dashboard

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

class AssignmentTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Assignment Deadline Tracker")
        self.root.geometry("900x620")
        self.service = AssignmentService()
        self.page = 1
        self.page_size = 10
        self._build()
        self.refresh()

    @staticmethod
    def _fresh_path():
        from pathlib import Path
        return Path.home() / ".assignment_deadline_tracker" / "assignments.json"

    def _build(self):
        ttk.Label(self.root, text="Assignment Deadline Tracker", font=("Arial", 19, "bold")).pack(pady=10)
        form = ttk.Frame(self.root, padding=8); form.pack(fill="x")
        self.entries = {}
        fields = [("Title", "title"), ("Subject", "subject"), ("Due date (YYYY-MM-DD)", "due_date")]
        for row, (label, key) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=4)
            entry = ttk.Entry(form, width=28); entry.grid(row=row, column=1, padx=5, pady=4); self.entries[key] = entry
        ttk.Label(form, text="Priority").grid(row=0, column=2, padx=5)
        self.priority = tk.StringVar(value="Medium")
        ttk.Combobox(form, textvariable=self.priority, values=["Low", "Medium", "High"], state="readonly", width=15).grid(row=0, column=3)
        ttk.Button(form, text="Add assignment", command=self.add).grid(row=1, column=2, padx=5)
        ttk.Button(form, text="Mark completed", command=self.complete).grid(row=1, column=3, padx=5)
        ttk.Button(form, text="Delete", command=self.delete).grid(row=2, column=2, padx=5)
        ttk.Button(form, text="Analytics", command=self.analytics).grid(row=2, column=3, padx=5)
        search = ttk.Frame(self.root, padding=8); search.pack(fill="x")
        ttk.Label(search, text="Search title/subject:").pack(side="left")
        self.query = tk.StringVar(); ttk.Entry(search, textvariable=self.query, width=28).pack(side="left", padx=6)
        self.status_filter = tk.StringVar(value="All")
        ttk.Combobox(search, textvariable=self.status_filter, values=["All", "Pending", "Completed"], state="readonly", width=12).pack(side="left")
        ttk.Button(search, text="Search", command=self.refresh).pack(side="left", padx=5)
        ttk.Button(search, text="Clear", command=self.clear_search).pack(side="left")
        self.tree = ttk.Treeview(self.root, columns=("title", "subject", "due", "priority", "status"), show="headings", height=15)
        for key, label, width in [("title","Title",220),("subject","Subject",150),("due","Due date",110),("priority","Priority",90),("status","Status",100)]:
            self.tree.heading(key, text=label); self.tree.column(key, width=width)
        self.tree.pack(fill="both", expand=True, padx=10, pady=8)
        nav = ttk.Frame(self.root); nav.pack(pady=5)
        ttk.Button(nav, text="Previous", command=lambda: self.change_page(-1)).pack(side="left", padx=5)
        self.page_label = ttk.Label(nav, text="Page 1"); self.page_label.pack(side="left", padx=8)
        ttk.Button(nav, text="Next", command=lambda: self.change_page(1)).pack(side="left", padx=5)

    def refresh(self):
        results = self.service.search(self.query.get(), self.status_filter.get())
        self.filtered = results
        items, self.page, pages = self.service.page(results, self.page, self.page_size)
        self.tree.delete(*self.tree.get_children())
        for item in items:
            self.tree.insert("", "end", iid=item.id, values=(item.title, item.subject, item.due_date, item.priority,
                                                                           "OVERDUE" if item.is_overdue else item.status))
        self.page_label.config(text=f"Page {self.page}/{pages} | {len(results)} result(s)")

    def change_page(self, delta): self.page += delta; self.refresh()
    def clear_search(self): self.query.set(""); self.status_filter.set("All"); self.page = 1; self.refresh()
    def selected_index(self):
        selected = self.tree.selection()
        if not selected: raise ValueError("Select an assignment first.")
        return selected[0]
    def add(self):
        try:
            self.service.add(self.entries["title"].get(), self.entries["subject"].get(), self.entries["due_date"].get(), self.priority.get())
            for entry in self.entries.values(): entry.delete(0, tk.END)
            self.page = 1; self.refresh(); messagebox.showinfo("Saved", "Assignment added successfully.")
        except (ValueError, StorageError) as exc: messagebox.showerror("Cannot add", str(exc))
    def complete(self):
        try: self.service.complete(self.selected_index()); self.refresh()
        except (ValueError, IndexError, StorageError) as exc: messagebox.showerror("Cannot update", str(exc))
    def delete(self):
        try:
            index = self.selected_index()
            if messagebox.askyesno("Confirm", "Delete the selected assignment?"):
                self.service.delete(index); self.refresh()
        except (ValueError, IndexError, StorageError) as exc: messagebox.showerror("Cannot delete", str(exc))
    def analytics(self):
        stats = self.service.analytics()
        messagebox.showinfo("Analytics", f"Total: {stats['total']}\nPending: {stats['pending']}\nCompleted: {stats['completed']}\nOverdue: {stats['overdue']}\nDue in 7 days: {stats['due_next_7_days']}\nCompletion: {stats['completion_rate']}%")
        if messagebox.askyesno("Export chart", "Would you like to export a Matplotlib dashboard?"):
            try: messagebox.showinfo("Chart exported", str(create_dashboard(self.service)))
            except (RuntimeError, ValueError, OSError) as exc: messagebox.showerror("Chart error", str(exc))

def main():
    root = tk.Tk()
    try:
        AssignmentTrackerApp(root)
    except StorageError as exc:
        messagebox.showerror("Data error", str(exc))
        root.destroy()
        return
    root.mainloop()

if __name__ == "__main__": main()
