"""Step 5: a web page with both agents side by side.

Run:  PORT=7860 ./cuga-docker.sh python playground/web.py
Open: http://localhost:7860

One visitor at a time: this is a local teaching version. The Hugging Face Space adds per-visitor sessions.
"""

import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from agents import answer_approval, ask, make_agent
from oak_tools import bills, reset_data
from scenarios import SCENARIOS, check_rules

state = {"agents": {}, "pending": None, "lock": asyncio.Lock()}


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["agents"] = {"without": await make_agent(False), "with": await make_agent(True)}
    yield
    for agent in state["agents"].values():
        await agent.aclose()


app = FastAPI(lifespan=lifespan)


class Ask(BaseModel):
    message: str = Field(min_length=1, max_length=600)


class Decision(BaseModel):
    approve: bool


def _scenario(message: str) -> dict:
    """Use the scenario's rules when the message is one of the buttons. Free text gets the general rules."""
    for sc in SCENARIOS:
        if sc["message"] == message:
            return sc
    return {"rules": ["approval", "denied_claim"]}


def _side(out: dict, message: str, approvals: int) -> dict:
    out = {**out, "approvals": approvals, "bills": bills()}
    out["broken"] = [] if out["paused"] else check_rules(_scenario(message), out)
    return out


@app.get("/")
def page():
    return FileResponse(Path(__file__).parent / "index.html")


@app.get("/api/scenarios")
def scenarios():
    return [{"id": s["id"], "label": s["label"], "message": s["message"]} for s in SCENARIOS]


@app.post("/api/ask")
async def api_ask(body: Ask):
    if state["lock"].locked():
        raise HTTPException(409, "A message is still running.")
    async with state["lock"]:
        reset_data()
        left = _side(await ask(state["agents"]["without"], body.message), body.message, 0)
        reset_data()
        right_raw = await ask(state["agents"]["with"], body.message)
        right = _side(right_raw, body.message, 1 if right_raw["paused"] else 0)
        state["pending"] = {"thread_id": right["thread_id"], "message": body.message,
                            "tools": right["tools"], "approvals": right["approvals"]} if right["paused"] else None
        return {"without": left, "with": right}


@app.post("/api/approve")
async def api_approve(body: Decision):
    pending = state["pending"]
    if not pending:
        raise HTTPException(409, "Nothing is waiting for approval.")
    async with state["lock"]:
        out = await answer_approval(state["agents"]["with"], pending["thread_id"], body.approve)
        out["tools"] = pending["tools"] + out["tools"]
        approvals = pending["approvals"] + (1 if out["paused"] else 0)
        state["pending"] = {**pending, "tools": out["tools"], "approvals": approvals} if out["paused"] else None
        return {"with": _side(out, pending["message"], approvals)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))
