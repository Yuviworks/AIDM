# Proactive maintenance proposals

## What this adds

- A daily background scan calculates the configured maintenance date for each registered appliance.
- When an appliance is due now or within the reminder window, AIDM creates one pending proposal per appliance/maintenance cycle.
- The dashboard shows the proposed date and demo service slot. The user must explicitly confirm before AIDM creates a confirmed booking.
- Declining a proposal does not create a booking.
- The scan is idempotent for a given appliance and due date.

## Configuration

Set `MAINTENANCE_REMINDER_DAYS=7` in the environment to propose maintenance seven days before the calculated due date. A value of `0` means only already-due maintenance is proposed. The default is 7.

The scheduler runs once at application startup and then every 24 hours. For local development, the dashboard's **Check maintenance now** button calls `POST /maintenance-proposals/scan`.

## Demo limitations

- Service-center names, locations, and slots currently come from `data/service_centers.json`; they are demo data, not verified KENT provider inventory.
- The current auto-assignment uses Pune and the nearest configured center because appliance records do not yet store a service location.
- Confirming a proposal records a booking in AIDM only. No real KENT system is contacted, and no SMS, email, technician dispatch, or provider notification is sent.
- This is interval-based scheduled maintenance, not a trained failure-prediction model.
- The current app's user identity is based on a client-supplied `user_id`. Do not deploy publicly until authentication, authorization, and ownership checks are added.

## API

- `POST /maintenance-proposals/scan` — run a scan manually.
- `GET /maintenance-proposals/user/{user_id}` — list a user's proposals.
- `POST /maintenance-proposals/{proposal_id}/respond?user_id={user_id}&decision=confirm` — confirm a pending proposal and create a booking.
- `POST /maintenance-proposals/{proposal_id}/respond?user_id={user_id}&decision=decline` — decline without booking.

The new `maintenance_proposals` table is created by SQLAlchemy on application startup. Existing user/appliance/booking records are not intentionally changed.
