from datetime import date


def validate_date(value: str) -> bool:
    try:
        return date.fromisoformat(value).isoformat() == value
    except (TypeError, ValueError):
        return False


def validate_priority(value: str) -> bool:
    return isinstance(value, str) and value.strip().title() in {"Low", "Medium", "High"}


def validate_text(value: str, field: str = "Value", max_length: int = 120) -> str:
    cleaned = value.strip() if isinstance(value, str) else ""
    if not cleaned:
        raise ValueError(f"{field} cannot be empty.")
    if len(cleaned) > max_length:
        raise ValueError(f"{field} must be {max_length} characters or fewer.")
    if any(ord(ch) < 32 for ch in cleaned):
        raise ValueError(f"{field} contains unsupported control characters.")
    return cleaned
