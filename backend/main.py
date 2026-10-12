from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from . import models

from .routers import auth
from .routers import appliances
from .routers import maintenance
from .routers import rag
from .routers import service
from .routers import booking
from .routers import agent


app = FastAPI(
    title="AIDM - Agentic AI Predictive Maintenance",
    description="Intelligent appliance maintenance and service management system",
    version="1.0.0"
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


@app.get("/")
def root():
    return {
        "message": "AIDM API is running",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }