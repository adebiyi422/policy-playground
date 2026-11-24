"""Shared helpers: build the agent with or without policies, ask it something, answer an approval."""

from __future__ import annotations

import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from cuga import CugaAgent
from cuga.backend.cuga_graph.nodes.human_in_the_loop.followup_model import ActionResponse, ActionType
from cuga.backend.cuga_graph.policy.configurable import create_agent_policy_system

from oak_tools import USER_CONTEXT, make_tools

POLICY_FOLDER = Path(__file__).parent / "policies"


async def make_agent(with_policies: bool) -> CugaAgent:
    """Same model, same tools, same prompt. Only the policies differ."""
    # Each agent gets its own policy store. Without this, CUGA shares one store between agents
    # in the same process, and the agent "without policies" would follow the other one's policies.
    store = await create_agent_policy_system(agent_id="oak-with-policies" if with_policies else "oak-without-policies")
    agent = CugaAgent(
        tools=make_tools(),
        policy_system=store,
        enable_knowledge=False,
        cuga_folder=tempfile.mkdtemp(prefix="cuga-"),  # private scratch folder per agent
        auto_load_policies=False,
        filesystem_sync=False,
    )
    # Start from an empty store, so nothing is left over from an earlier run.
    await agent.policies.clear()
    if with_policies:
        loaded = await agent.policies.load_from_folder(str(POLICY_FOLDER))
        if loaded.get("errors"):
            raise RuntimeError(f"Policy files failed to load: {loaded['errors']}")
    count = len(await agent.policies.list())
    print(f"Agent {'WITH' if with_policies else 'WITHOUT'} policies: {count} policies active")
    if with_policies != (count > 0):
        raise RuntimeError("The agent has the wrong policies loaded")
    return agent


def _names(tool_calls) -> list:
    return [(c.get("name") if isinstance(c, dict) else getattr(c, "name", str(c))).replace("oak_health_insurance_", "")
            for c in tool_calls]


async def _paused(agent: CugaAgent, thread_id: str, answer: str) -> bool:
    if "paused for approval" in answer:
        return True
    state = await agent.graph.aget_state({"configurable": {"thread_id": thread_id}})
    return bool(state.next)  # steps still waiting = the run is on hold


def _summary(result, paused: bool) -> dict:
    return {
        "answer": result.answer,
        "tools": _names(result.tool_calls),
        "paused": paused,
        "policies": [f"{d.policy_name or d.policy_id}: {getattr(d.outcome, 'value', d.outcome)}" for d in (result.policy_decisions or [])
                     if getattr(d, "policy_id", None)],
        "error": result.error,
    }


async def ask(agent: CugaAgent, message: str, thread_id: str | None = None) -> dict:
    thread_id = thread_id or uuid.uuid4().hex
    result = await agent.invoke(message, thread_id=thread_id, user_context=USER_CONTEXT, track_tool_calls=True)
    out = _summary(result, await _paused(agent, thread_id, result.answer))
    out["thread_id"] = thread_id
    return out


async def answer_approval(agent: CugaAgent, thread_id: str, approve: bool) -> dict:
    """Resume a paused run on the same thread with the member's decision."""
    decision = ActionResponse(action_id="tool_approval", response_type=ActionType.CONFIRMATION,
                              confirmed=approve, timestamp=datetime.now().isoformat())
    result = await agent.invoke(None, thread_id=thread_id, action_response=decision, track_tool_calls=True)
    out = _summary(result, await _paused(agent, thread_id, result.answer))
    out["thread_id"] = thread_id
    return out


def show(title: str, out: dict) -> None:
    print(f"\n===== {title} =====")
    print("Tools called:", out["tools"] or "none")
    if out["policies"]:
        print("Policies:", out["policies"])
    if out["paused"]:
        print("STATUS: paused, waiting for approval")
    if out["error"]:
        print("ERROR:", out["error"])
    print(out["answer"])
