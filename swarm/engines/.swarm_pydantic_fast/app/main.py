from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app.agents.registry import build_all_agents
from app.api.routes import router as swarm_router
from app.api.websocket import swarm_websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    build_all_agents()
    yield


app = FastAPI(
    title="SWARN - FastAPI + PydanticAI",
    description="Sequential multi-agent pipeline orchestrator",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(swarm_router)


@app.websocket("/swarm/ws")
async def websocket_endpoint(ws: WebSocket):
    await swarm_websocket(ws)


@app.get("/")
async def root():
    return {
        "service": "SWARN",
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }
