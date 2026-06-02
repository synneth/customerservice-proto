"""FastAPI backend for Mote & Mer AI kundeservice prototype."""

from __future__ import annotations
import os
import json
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from tools import TOOL_HANDLERS
from agent_config import SYSTEM_PROMPT, TOOLS

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

app = FastAPI(title="Mote & Mer Kundeservice API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Tool webhook endpoints — called by ElevenLabs agent
# ---------------------------------------------------------------------------

@app.post("/tools/{tool_name}")
async def handle_tool(tool_name: str, request: Request) -> JSONResponse:
    handler = TOOL_HANDLERS.get(tool_name)
    if not handler:
        raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_name}")
    try:
        body = await request.json()
    except Exception:
        body = {}
    result = handler(body)
    return JSONResponse(content=result)


# ---------------------------------------------------------------------------
# Conversation token — frontend asks backend for a signed URL
# ---------------------------------------------------------------------------

@app.get("/api/conversation-token")
async def get_conversation_token() -> JSONResponse:
    if not ELEVENLABS_API_KEY:
        raise HTTPException(status_code=500, detail="ELEVENLABS_API_KEY ikke konfigurert.")
    if not AGENT_ID:
        raise HTTPException(status_code=500, detail="ELEVENLABS_AGENT_ID ikke konfigurert.")

    url = f"https://api.elevenlabs.io/v1/convai/conversation/get_signed_url?agent_id={AGENT_ID}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers={"xi-api-key": ELEVENLABS_API_KEY})
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return JSONResponse(content=resp.json())


# ---------------------------------------------------------------------------
# Agent setup helper — creates or updates the ElevenLabs agent
# ---------------------------------------------------------------------------

@app.post("/api/setup-agent")
async def setup_agent() -> JSONResponse:
    """Creates the ElevenLabs Conversational AI agent with correct config."""
    if not ELEVENLABS_API_KEY:
        raise HTTPException(status_code=500, detail="ELEVENLABS_API_KEY ikke konfigurert.")

    tools_with_url = []
    for tool in TOOLS:
        t = json.loads(json.dumps(tool))
        t["api"]["url"] = t["api"]["url"].replace("{BACKEND_URL}", BACKEND_URL)
        tools_with_url.append(t)

    payload = {
        "name": "Mote & Mer Kundeservice",
        "conversation_config": {
            "agent": {
                "prompt": {
                    "prompt": SYSTEM_PROMPT,
                    "llm": "claude-sonnet-4-6",
                    "tools": tools_with_url,
                },
                "first_message": (
                    "Hei, du har ringt til Mote & Mer sin kundeservice. "
                    "Jeg er din digitale assistent. Hva kan jeg hjelpe deg med i dag?"
                ),
                "language": "no",
            },
            "tts": {
                "model_id": "eleven_turbo_v2_5",
                "voice_id": "cgSgspJ2msm6clMCkdW9",  # default — swap in dashboard
            },
        },
    }

    async with httpx.AsyncClient() as client:
        if AGENT_ID:
            resp = await client.patch(
                f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}",
                json=payload,
                headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
            )
        else:
            resp = await client.post(
                "https://api.elevenlabs.io/v1/convai/agents/create",
                json=payload,
                headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
            )

    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    data = resp.json()
    agent_id = data.get("agent_id", AGENT_ID)
    return JSONResponse(content={
        "agent_id": agent_id,
        "melding": f"Agent konfigurert. Legg til ELEVENLABS_AGENT_ID={agent_id} i .env",
    })


# ---------------------------------------------------------------------------
# Serve frontend
# ---------------------------------------------------------------------------

frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
