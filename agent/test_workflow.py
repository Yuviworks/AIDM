from .workflow import aidm_workflow


if __name__ == "__main__":

    initial_state = {
    "user_id": 1,
    "appliance_id": 1,
    "location": "Pune",

    "selected_service_center": 1,
    "booking_date": "2026-09-29",

    "confirm_booking": True
}

    print("\nRunning AIDM Agent...\n")

    result = aidm_workflow.invoke(initial_state)

    print("================================")
    print("AIDM AGENT RESULT")
    print("================================")

    print("\nMaintenance Status:")
    print(result.get("maintenance_status"))

    print("\nMaintenance Explanation:")
    print(result.get("maintenance_explanation"))

    print("\nService Centers:")

    for center in result.get("service_centers", []):
        print(
            f"- {center['name']} | "
            f"{center['location']} | "
            f"{center['availability']}"
        )

    print("\nBooking Status:")
    print(result.get("booking_status"))

    print("\nBooking ID:")
    print(result.get("booking_id"))