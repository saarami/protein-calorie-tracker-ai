from __future__ import annotations

from app.db.base_class import Base

# Import models so SQLAlchemy metadata is populated
from app.models.user import User  # noqa: F401,E402
from app.models.meal import Meal  # noqa: F401,E402
from app.models.meal_item import MealItem  # noqa: F401,E402
from app.models.telegram_link import TelegramLink  # noqa: F401,E402
from app.models.telegram_link_code import TelegramLinkCode  # noqa: F401,E402
