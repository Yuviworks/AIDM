# AIDM — Intelligent Maintenance Dashboard

AIDM is a maintenance-support application for KENT water purifiers. The project combines a web dashboard, a FastAPI backend, a SQLite database, service-booking workflows, and an Ask AIDM knowledge assistant.

## Current project areas

- **Frontend:** HTML, CSS, and JavaScript dashboard under `frontend/`.
- **Backend:** FastAPI API and maintenance-related services under `backend/`.
- **Agent / RAG:** Agent and retrieval-augmented knowledge assistant code in `agent/` and `rag/`.
- **Data and manuals:** Demo data and reference manuals in `data/` and `manuals/`.

## Current status

- The navy-and-teal dashboard theme override has been added to `frontend/css/style.css`, while preserving the existing layout rules.
- Maintenance proposal generation and approve/decline flows have been implemented and tested locally in the development environment, but the latest local proposal UI changes have not yet been synchronized to the GitHub dashboard files.
- Service-center information currently includes demo data; contact details and appointment slots must be verified before production use.
- A validated predictive-maintenance model is still planned work.
- Security, booking concurrency, and scheduler deployment hardening remain to be completed.

## Local setup

Check the dependencies and configuration used by your current development environment before running the project. Typical development steps are:

1. Clone this repository.
2. Create and activate a Python virtual environment.
3. Install the project's Python dependencies from its dependency file, if present.
4. Configure required environment variables locally; do not commit secrets.
5. Start the FastAPI backend using the project's entry point.
6. Serve/open the frontend using the project's expected local setup and verify the API URL matches the backend.

Refer to the actual project files for the authoritative startup commands and configuration. Do not commit local databases, credentials, virtual environments, caches, or `.env` files.

## Next development priorities

See [AIDM_NEXT_SESSION.md](AIDM_NEXT_SESSION.md) for the detailed handoff checklist. Highest priorities:

1. Verify the navy-and-teal theme in the browser and test responsive layouts.
2. Synchronize and test the latest local dashboard proposal UI changes.
3. Improve authorization, duplicate-slot protection, and scheduler behavior.
4. Replace demo service-center details with verified information.
5. Collect historical maintenance data and evaluate a predictive model before using it in recommendations.
6. Add automated tests and prepare production configuration.

## Development approach

Make changes incrementally, test locally, review the diff, and only then commit. Never publish credentials, personal data, or a local development database.
