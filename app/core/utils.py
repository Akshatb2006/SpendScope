from typing import Optional

def calculate_percentage(current: float, total: float) -> float:
    return (current / total * 100) if total > 0 else 0

def truncate_string(s: str, max_length: int = 100) -> str:
    return s[:max_length] + "..." if len(s) > max_length else s