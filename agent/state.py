from typing import TypedDict, List, Dict, Optional


class AgentState(TypedDict, total=False):

    # User / appliance
    user_id: int
    appliance_id: int
    location: str

    # User question
    user_question: Optional[str]

    # Maintenance
    maintenance_status: str
    maintenance_explanation: str
    next_maintenance_date: Optional[str]

    # Service discovery
    service_centers: List[Dict]

    # Agent recommendation
    recommended_service_center: Optional[Dict]
    recommended_slot: Optional[str]

    # User selection / confirmation
    selected_service_center: Optional[int]
    booking_date: Optional[str]
    booking_slot: Optional[str]
    confirm_booking: bool


    # Booking
    booking_id: Optional[int]
    booking_status: Optional[str]