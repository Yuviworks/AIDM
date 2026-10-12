from datetime import date
from dateutil.relativedelta import relativedelta


def calculate_maintenance(appliance):

    next_maintenance_date = (
        appliance.last_service_date
        + relativedelta(
            months=appliance.maintenance_interval
        )
    )

    today = date.today()

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
        "maintenance_interval_months":
            appliance.maintenance_interval,
        "status": status
    }