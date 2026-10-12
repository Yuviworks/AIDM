# AIDM — Project Handoff Notes

_Last updated: 13 October 2026_

To resume work, attach this file in ChatGPT and say: **“Continue AIDM using this handoff file.”**

## Project overview

AIDM is a maintenance-support system for KENT water purifiers. It uses a FastAPI backend, SQLite, and an HTML/CSS/JavaScript frontend. The user prefers incremental changes in VS Code with local testing after each step.

## Current status

### Backend
- Models include `User`, `Appliance`, `Booking`, and `MaintenanceProposal`.
- Database used locally: `database/aidm.db`.
- Proposal uniqueness is defined for `(appliance_id, maintenance_due_date)`.
- Service-center data comes from `data/service_centers.json`.
- Proposal endpoints implemented locally:
  - `POST /maintenance-proposals/scan`
  - `GET /maintenance-proposals/user/{user_id}`
  - `POST /maintenance-proposals/{proposal_id}/approve?user_id=...`
  - `POST /maintenance-proposals/{proposal_id}/decline?user_id=...`
- Scanning calculates a due date from the last service date and maintenance interval, then creates a pending proposal if one does not exist.
- Approval creates a confirmed booking and marks the proposal approved; decline marks it declined.
- Scheduler runs on startup and repeats every 60 minutes.
- These workflows were tested locally; example IDs in the local database may change.

### Backend limitations
- Add transaction-level protection against simultaneous bookings for the same slot.
- Review authentication and ownership checks; do not rely only on a user ID supplied by the client.
- Prevent duplicate scheduler execution if multiple app workers are used.
- Verify demo service-center details, phone numbers, and slots before production use.

### Frontend
- Main files: `frontend/dashboard.html`, `frontend/js/dashboard.js`, and `frontend/css/style.css`.
- The original CSS contains the dashboard layout and responsive rules for the navbar, hero, appliances, maintenance, agent workflow, booking confirmation, service centers, history, and Ask AIDM.
- A navy-and-teal theme override has now been committed to GitHub in `frontend/css/style.css`.
- The visual result has not yet been confirmed in the browser. Keep the original layout CSS and test the new colors and focus styles.
- **GitHub synchronization gap:** the current GitHub copies of `frontend/dashboard.html` and `frontend/js/dashboard.js` did not contain the local maintenance-proposal UI functions/section when checked on 13 October 2026. Do not assume all local changes have been pushed. Compare with the user's local files and synchronize carefully.

## Remaining work — prioritized

### Priority 1: Verify dashboard redesign
- [ ] Run the app locally and inspect the navy-and-teal theme.
- [ ] Check navbar, hero, appliance cards, maintenance cards, agent workflow, Ask AIDM, service centers, and history.
- [ ] Verify maintenance proposal cards and pending/approved/declined states.
- [ ] Test desktop, tablet, and mobile widths.
- [ ] Fix CSS/Bootstrap conflicts and verify keyboard focus styles.
- [ ] Confirm buttons and forms still work.

### Priority 2: Synchronize local frontend changes to GitHub
- [ ] Compare local `dashboard.html` and `dashboard.js` with the remote files.
- [ ] Confirm the proposal section and functions are present and working locally.
- [ ] Review diffs before replacing remote files; preserve any remote-only changes.
- [ ] Commit only intended source files.

### Priority 3: Proposal and booking reliability
- [ ] Test different users and appliance models, repeated scans, overdue, due-soon, and not-yet-due cases.
- [ ] Enforce proposal ownership and authentication.
- [ ] Prevent duplicate/conflicting bookings with database transactions and suitable constraints.
- [ ] Review scheduler behavior under multiple workers.
- [ ] Improve logging and failure responses.

### Priority 4: Real service-center information
- [ ] Verify service-center names, addresses, contact details, and appointment availability.
- [ ] Remove placeholder phone numbers and unverified slots.
- [ ] Handle no matching center, no available slot, and booking failures.

### Priority 5: Predictive maintenance
The predictive model has not been built.
- [ ] Define the event/outcome and prediction horizon.
- [ ] Collect representative appliance/service history, symptoms, filter changes, technician findings, repair actions, and outcomes.
- [ ] Design structured owner/technician data collection.
- [ ] Clean and validate data; avoid target leakage.
- [ ] Establish a baseline and evaluate on held-out data.
- [ ] Integrate only after performance is validated and uncertainty is handled appropriately.

### Priority 6: Testing and production readiness
- [ ] Add automated API tests for scan, list, approve, decline, and slot conflicts.
- [ ] Test frontend/backend integration and error states.
- [ ] Review database consistency, configuration, secrets, logging, and deployment.
- [ ] Document setup and architecture; prepare a repeatable demo.

## GitHub and security notes
- Repository: [Yuviworks/AIDM](https://github.com/Yuviworks/AIDM), default branch `main`.
- The theme override has been pushed to `frontend/css/style.css`.
- A README and this handoff file are being added to document status and next steps.
- Never commit local SQLite databases, secrets, API keys, `.env` files, virtual environments, caches, or personal data.
- Make changes incrementally and inspect the diff before committing.

## Next-session starting point

Start by running the app and verifying the new theme in the browser. Then compare the user's local `dashboard.html` and `dashboard.js` with GitHub, synchronize the proposal UI carefully, and continue down the priorities above.
