
import asyncio
import logging

from .database import SessionLocal
from .routers.maintenance_proposals import scan_due_maintenance


logger = logging.getLogger("aidm.scheduler")

# Run the maintenance scan every 60 minutes.
SCAN_INTERVAL_SECONDS = 60 * 60


def run_maintenance_scan() -> None:
    """Run one scan using a dedicated database session."""
    db = SessionLocal()

    try:
        result = scan_due_maintenance(
            user_id=None,
            db=db,
        )

        logger.info(
            "Scheduled maintenance scan completed: %s",
            result,
        )
    except Exception:
        logger.exception(
            "Scheduled maintenance scan failed"
        )
    finally:
        db.close()


async def maintenance_scheduler() -> None:
    """
    Scan immediately, then repeat every 60 minutes.

    The database work runs in a worker thread so it does not
    block FastAPI's asynchronous event loop.
    """
    logger.info("Maintenance scheduler started")

    while True:
        await asyncio.to_thread(run_maintenance_scan)
        await asyncio.sleep(SCAN_INTERVAL_SECONDS)
