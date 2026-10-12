
from datetime import date
from dateutil.relativedelta import relativedelta


def calculate_maintenance(appliance):
    """
    Calculate the next maintenance date and current maintenance status.
    """

    next_maintenance_date = (
        appliance.last_service_date
        + relativedelta(
            months=appliance.maintenance_interval
        )
    )

    today = date.today()

    days_until_maintenance = (
        next_maintenance_date - today
    ).days

    maintenance_due = today >= next_maintenance_date

    if maintenance_due:
        status = "MAINTENANCE_DUE"
    else:
        status = "UPCOMING"

    return {
        "appliance_id": appliance.id,
        "appliance": appliance.appliance_type,
        "brand": appliance.brand,
        "model": appliance.model,
        "last_service_date": appliance.last_service_date,
        "next_maintenance_date": next_maintenance_date,
        "maintenance_interval_months": (
            appliance.maintenance_interval
        ),
        "days_until_maintenance": days_until_maintenance,
        "status": status,
    }
