from __future__ import annotations

import re


def _is_hebrew(text: str) -> bool:
    return bool(re.search(r"[\u0590-\u05FF]", text))


def meal_added_message(input_text: str, title: str, total_cal: int, total_pro: float, items: list[dict]) -> str:
    heb = _is_hebrew(input_text)
    if heb:
        lines = [
            "🍽️ נוספה ארוחה",
            f"{title}",
            f"{total_cal} kcal | {round(total_pro, 1)} g protein",
            "",
            "רכיבים:",
        ]
    else:
        lines = [
            "🍽️ Meal added",
            f"{title}",
            f"{total_cal} kcal | {round(total_pro, 1)} g protein",
            "",
            "Items:",
        ]

    for it in items:
        name = it["name"]
        qty = it.get("quantity")
        unit = it.get("unit")
        prefix = ""
        if qty is not None:
            if unit:
                prefix = f"{qty:g} {unit} "
            else:
                prefix = f"{qty:g} "
        lines.append(f"- {prefix}{name}: {int(it['calories'])} kcal | {round(float(it['protein_g']), 1)} g")
    return "\n".join(lines)


def today_summary_message(input_text: str, meals_count: int, total_cal: int, total_pro: float) -> str:
    heb = _is_hebrew(input_text)
    if heb:
        return "\n".join([
            "📅 סיכום היום",
            f"{meals_count} ארוחות",
            f"{total_cal} kcal | {round(total_pro, 1)} g protein",
        ])
    return "\n".join([
        "📅 Today summary",
        f"{meals_count} meals",
        f"{total_cal} kcal | {round(total_pro, 1)} g protein",
    ])
