import datetime
from typing import Any

def day_summary_key(user_id: Any, date: datetime.date) -> str:
    return f"day_summary:v1:{user_id}:{date.isoformat()}"
