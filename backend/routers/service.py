from fastapi import APIRouter

from ..services.service_service import find_service_centers


router = APIRouter(
    prefix="/service",
    tags=["Service Discovery"]
)


@router.get("/centers")
def get_service_centers(
    brand: str,
    location: str
):
    centers = find_service_centers(
        brand=brand,
        location=location
    )

    return {
        "brand": brand,
        "location": location,
        "count": len(centers),
        "service_centers": centers
    }