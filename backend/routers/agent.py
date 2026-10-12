from fastapi import APIRouter, HTTPException

from agent.workflow import aidm_workflow


router = APIRouter(
    prefix="/agent",
    tags=["AIDM Agent"]
)


@router.post("/run")
def run_agent(
    user_id: int,
    appliance_id: int,
    location: str = "Pune",
    user_question: str | None = None,
    selected_service_center: int | None = None,
    booking_date: str | None = None,
    booking_slot: str | None = None,
    confirm_booking: bool = False
):

    try:

        state = {
            "user_id": user_id,
            "appliance_id": appliance_id,
            "location": location,

            "user_question": user_question,

            "selected_service_center":
                selected_service_center,

            "booking_date":
                booking_date,

            "booking_slot":
                booking_slot,

            "confirm_booking":
                confirm_booking
        }


        result = aidm_workflow.invoke(
            state
        )


        return {

            "status":
                "success",


            # =========================
            # MAINTENANCE
            # =========================

            "maintenance_status":
                result.get(
                    "maintenance_status"
                ),


            "next_maintenance_date":
                result.get(
                    "next_maintenance_date"
                ),


            # =========================
            # RAG
            # =========================

            "maintenance_explanation":
                result.get(
                    "maintenance_explanation"
                ),


            # =========================
            # SERVICE DISCOVERY
            # =========================

            "service_centers":
                result.get(
                    "service_centers",
                    []
                ),


            # =========================
            # AGENT RECOMMENDATION
            # =========================

            "recommended_service_center":
                result.get(
                    "recommended_service_center"
                ),


            "recommended_slot":
                result.get(
                    "recommended_slot"
                ),


            # =========================
            # BOOKING
            # =========================

            "booking_id":
                result.get(
                    "booking_id"
                ),


            "booking_status":
                result.get(
                    "booking_status"
                ),


            "booking_date":
                result.get(
                    "booking_date"
                ),


            "booking_slot":
                result.get(
                    "booking_slot"
                )

        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )