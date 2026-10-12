from langgraph.graph import StateGraph, START, END
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import Appliance

from .state import AgentState

from .tools import (
    maintenance_tool,
    rag_tool,
    service_discovery_tool,
    nearest_service_center_tool,
    available_slot_tool,
    booking_tool
)


# ============================================================
# MAINTENANCE NODE
# ============================================================

def maintenance_node(state: AgentState):

    db: Session = SessionLocal()

    try:

        appliance = db.query(Appliance).filter(
            Appliance.id == state["appliance_id"]
        ).first()

        if not appliance:

            return {
                "maintenance_status": "ERROR",
                "maintenance_explanation":
                    "Appliance not found."
            }

        result = maintenance_tool(appliance)

        return {

            "maintenance_status":
                result["status"],

            "next_maintenance_date":
                str(
                    result["next_maintenance_date"]
                )

        }

    finally:

        db.close()


# ============================================================
# RAG / EXPLANATION NODE
# ============================================================

def rag_node(state: AgentState):
    db: Session = SessionLocal()

    try:
        appliance = db.query(Appliance).filter(
            Appliance.id == state["appliance_id"]
        ).first()

        if not appliance:
            return {
                "maintenance_explanation": "Appliance not found."
            }

        user_question = state.get("user_question")

        if not user_question:
            user_question = (
                "Why does my water purifier require maintenance?"
            )

        result = rag_tool(
            query=user_question,
            model=appliance.model
        )

        return {
            "maintenance_explanation": result["answer"]
        }

    finally:
        db.close()


# ============================================================
# SERVICE DISCOVERY NODE
# ============================================================

def service_node(state: AgentState):

    db: Session = SessionLocal()

    try:

        appliance = db.query(Appliance).filter(
            Appliance.id == state["appliance_id"]
        ).first()

        if not appliance:

            return {
                "service_centers": []
            }

        centers = service_discovery_tool(

            brand=appliance.brand,

            location=state["location"]

        )

        return {

            "service_centers":
                centers

        }

    finally:

        db.close()


# ============================================================
# NEAREST SERVICE CENTER NODE
# ============================================================

def nearest_center_node(
    state: AgentState
):

    db: Session = SessionLocal()

    try:

        appliance = db.query(Appliance).filter(
            Appliance.id == state["appliance_id"]
        ).first()

        if not appliance:

            return {

                "recommended_service_center":
                    None

            }

        center = nearest_service_center_tool(

            brand=appliance.brand,

            location=state["location"]

        )

        return {

            "recommended_service_center":
                center

        }

    finally:

        db.close()


# ============================================================
# AVAILABLE SLOT NODE
# ============================================================

def slot_selection_node(
    state: AgentState
):

    center = state.get(
        "recommended_service_center"
    )

    maintenance_date = state.get(
        "next_maintenance_date"
    )

    if not center or not maintenance_date:

        return {

            "recommended_slot":
                None

        }

    slot = available_slot_tool(

        service_center=center,

        preferred_date=maintenance_date

    )

    return {

        "recommended_slot":
            slot

    }


# ============================================================
# CONFIRMATION ROUTER
# ============================================================

def confirmation_router(
    state: AgentState
):

    if state.get(
        "confirm_booking"
    ) is True:

        return "booking"

    return END


# ============================================================
# BOOKING NODE
# ============================================================

def booking_node(
    state: AgentState
):

    # --------------------------------------------------------
    # IMPORTANT:
    # Use the user's selected service center if provided.
    # Otherwise use the agent's recommended center.
    # --------------------------------------------------------

    selected_center_id = state.get(
        "selected_service_center"
    )

    recommended_center = state.get(
        "recommended_service_center"
    )

    service_centers = state.get(
        "service_centers",
        []
    )


    selected_center = None


    # --------------------------------------------------------
    # Find the user's selected center
    # --------------------------------------------------------

    if selected_center_id is not None:

        for center in service_centers:

            if center["id"] == selected_center_id:

                selected_center = center

                break


    # --------------------------------------------------------
    # If selected center wasn't found in the discovered
    # centers, fall back to recommended center.
    # --------------------------------------------------------

    if selected_center is None:

        selected_center = (
            recommended_center
        )


    # --------------------------------------------------------
    # Determine booking date
    # --------------------------------------------------------

    booking_date = state.get(
        "booking_date"
    )


    if not booking_date:

        booking_date = state.get(
            "next_maintenance_date"
        )


    # --------------------------------------------------------
    # Determine booking slot
    # --------------------------------------------------------

    booking_slot = state.get(
        "booking_slot"
    )


    if not booking_slot:

        booking_slot = state.get(
            "recommended_slot"
        )


    # --------------------------------------------------------
    # Validate service center
    # --------------------------------------------------------

    if not selected_center:

        return {

            "booking_status":
                "NO_SERVICE_CENTER"

        }


    # --------------------------------------------------------
    # Validate booking date
    # --------------------------------------------------------

    if not booking_date:

        return {

            "booking_status":
                "NO_BOOKING_DATE"

        }


    # --------------------------------------------------------
    # Validate booking slot
    # --------------------------------------------------------

    if not booking_slot:

        return {

            "booking_status":
                "NO_BOOKING_SLOT"

        }


    # --------------------------------------------------------
    # Validate selected slot belongs to selected center
    # --------------------------------------------------------

    available_slots = (
        selected_center.get(
            "available_slots",
            []
        )
    )


    if (
        available_slots
        and booking_slot not in available_slots
    ):

        return {

            "booking_status":
                "INVALID_BOOKING_SLOT"

        }


    # --------------------------------------------------------
    # Create booking
    # --------------------------------------------------------

    result = booking_tool(

        user_id=state["user_id"],

        appliance_id=state["appliance_id"],

        service_center_id=
            selected_center["id"],

        booking_date=
            booking_date,

        booking_slot=
            booking_slot

    )


    # --------------------------------------------------------
    # Return booking result
    # --------------------------------------------------------

    return {

        "booking_id":
            result["booking_id"],

        "booking_status":
            result["status"],

        "booking_date":
            result["booking_date"],

        "booking_slot":
            result["booking_slot"]

    }


# ============================================================
# BUILD LANGGRAPH WORKFLOW
# ============================================================

def build_workflow():

    graph = StateGraph(
        AgentState
    )


    # --------------------------------------------------------
    # Add Nodes
    # --------------------------------------------------------

    graph.add_node(
        "maintenance",
        maintenance_node
    )


    graph.add_node(
        "rag_explanation",
        rag_node
    )


    graph.add_node(
        "service_discovery",
        service_node
    )


    graph.add_node(
        "nearest_center",
        nearest_center_node
    )


    graph.add_node(
        "slot_selection",
        slot_selection_node
    )


    graph.add_node(
        "booking",
        booking_node
    )


    # --------------------------------------------------------
    # Workflow
    # --------------------------------------------------------

    graph.add_edge(
        START,
        "maintenance"
    )


    graph.add_edge(
        "maintenance",
        "rag_explanation"
    )


    graph.add_edge(
        "rag_explanation",
        "service_discovery"
    )


    graph.add_edge(
        "service_discovery",
        "nearest_center"
    )


    graph.add_edge(
        "nearest_center",
        "slot_selection"
    )


    # --------------------------------------------------------
    # Human confirmation
    # --------------------------------------------------------

    graph.add_conditional_edges(

        "slot_selection",

        confirmation_router,

        {

            "booking":
                "booking",

            END:
                END

        }

    )


    # --------------------------------------------------------
    # Booking → End
    # --------------------------------------------------------

    graph.add_edge(
        "booking",
        END
    )


    return graph.compile()


# ============================================================
# COMPILE WORKFLOW
# ============================================================

aidm_workflow = build_workflow()