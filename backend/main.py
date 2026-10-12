import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, SessionLocal, engine
from . import models
from .routers import auth, appliances, maintenance, rag, service, booking, agent, maintenance_proposals
from .routers.maintenance_proposals import generate_due_proposals

logger = logging.getLogger(__name__)


async def _maintenance_scan_loop():
    while True:
        db = SessionLocal()
        try:
            result = generate_due_proposals(db)
            logger.info("Proactive maintenance scan completed: %s", result)
        except Exception:
            logger.exception("Proactive maintenance scan failed")
        finally:
            db.close()
        await asyncio.sleep(24 * 60 * 60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    task = asyncio.create_task(_maintenance_scan_loop())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="AIDM - Agentic AI Predictive Maintenance",
    description="Intelligent appliance maintenance and service management system",
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(appliances.router)
app.include_router(maintenance.router)
app.include_router(rag.router)
app.include_router(service.router)
app.include_router(booking.router)
app.include_router(agent.router)
app.include_router(maintenance_proposals.router)


@app.get("/")
def root():
    return {"message": "AIDM API is running", "status": "success"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
