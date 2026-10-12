
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from . import models

from .routers import (
    auth,
    appliances,
    maintenance,
    rag,
    service,
    booking,
    agent,
    maintenance_proposals,
)

from .scheduler import maintenance_scheduler


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aidm.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start and stop the maintenance scheduler with the API."""
    scheduler_task = asyncio.create_task(
        maintenance_scheduler()
    )
    app.state.maintenance_scheduler_task = scheduler_task

    logger.info("AIDM application started")

    try:
        yield
    finally:
        scheduler_task.cancel()

        try:
            await scheduler_task
        except asyncio.CancelledError:
            logger.info("Maintenance scheduler stopped")

        logger.info("AIDM application shut down")


app = FastAPI(
    title="AIDM - Agentic AI Predictive Maintenance",
    description=(
        "Intelligent appliance maintenance and service management system"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

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
    return {
        "message": "AIDM API is running",
        "status": "success",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }
