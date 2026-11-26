"""Matplotlib visual reports. Install matplotlib to enable chart export."""
from pathlib import Path
from .service import AssignmentService


def create_dashboard(service: AssignmentService, output_path="reports/assignment_dashboard.png") -> Path:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("Matplotlib is not installed. Run: pip install matplotlib") from exc
    stats = service.analytics()
    path = Path(output_path).expanduser()
    if path.name != "assignment_dashboard.png":
        raise ValueError("Report filename must be assignment_dashboard.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].bar(["Pending", "Completed", "Overdue"],
                [stats["pending"], stats["completed"], stats["overdue"]])
    axes[0].set_title("Assignment Status")
    axes[0].set_ylabel("Number of assignments")
    priorities = ["Low", "Medium", "High"]
    axes[1].bar(priorities, [stats["priority_counts"].get(p, 0) for p in priorities])
    axes[1].set_title("Pending Assignments by Priority")
    axes[1].set_ylabel("Number of assignments")
    fig.suptitle(f"Assignment Deadline Tracker | Completion: {stats['completion_rate']}%")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path
