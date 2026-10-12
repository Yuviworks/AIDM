import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

SERVICE_CENTER_PATH = (
    BASE_DIR / "data" / "service_centers.json"
)


def load_service_centers():
    with open(
        SERVICE_CENTER_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def find_service_centers(
    brand: str,
    location: str
):

    service_centers = load_service_centers()

    results = []

    for center in service_centers:

        brand_match = (
            center["brand"].lower()
            == brand.lower()
        )

        location_match = (
            location.lower()
            in center["location"].lower()
        )

        if brand_match and location_match:

            results.append(center)

    return results


def find_nearest_service_center(
    brand: str,
    location: str
):

    centers = find_service_centers(
        brand=brand,
        location=location
    )

    if not centers:
        return None

    nearest_center = min(
        centers,
        key=lambda center: center.get(
            "distance_km",
            float("inf")
        )
    )

    return nearest_center


def find_available_slot(
    service_center: dict,
    preferred_date: str
):

    slots = service_center.get(
        "available_slots",
        []
    )

    for slot in slots:

        if slot.startswith(preferred_date):

            return slot

    return None