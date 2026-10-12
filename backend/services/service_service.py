
import json
from datetime import date, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

SERVICE_CENTER_PATH = (
    BASE_DIR / "data" / "service_centers.json"
)


def load_service_centers():
    with open(
        SERVICE_CENTER_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def find_service_centers(
    brand: str,
    location: str,
):
    service_centers = load_service_centers()
    results = []

    for center in service_centers:
        brand_match = (
            center["brand"].lower() == brand.lower()
        )

        location_match = (
            location.lower() in center["location"].lower()
        )

        if brand_match and location_match:
            results.append(center)

    return results


def find_nearest_service_center(
    brand: str,
    location: str,
):
    centers = find_service_centers(
        brand=brand,
        location=location,
    )

    if not centers:
        return None

    return min(
        centers,
        key=lambda center: center.get(
            "distance_km",
            float("inf"),
        ),
    )


def find_available_slot(
    service_center: dict,
    preferred_date: str,
):
    slots = service_center.get("available_slots", [])

    for slot in slots:
        if slot.startswith(preferred_date):
            return slot

    return None


def find_next_available_slot(
    service_center: dict,
    preferred_date: date,
    search_days: int = 30,
):
    """
    Find the earliest listed slot on or after preferred_date.

    The service center's available_slots must contain date-prefixed
    strings, such as '2026-11-15 10:00 AM'.
    """

    if search_days < 0:
        raise ValueError("search_days cannot be negative")

    slots = service_center.get("available_slots", [])
    earliest_slot = None
    earliest_date = None

    last_date = preferred_date + timedelta(days=search_days)

    for slot in slots:
        try:
            slot_date = date.fromisoformat(slot[:10])
        except (ValueError, TypeError):
            continue

        if preferred_date <= slot_date <= last_date:
            if earliest_date is None or slot_date < earliest_date:
                earliest_date = slot_date
                earliest_slot = slot

    return earliest_slot
