"""Oak Health Insurance tools for a CUGA agent.

The Oak Health API (package `cuga-oak-health`) is a FastAPI app. Instead of running it on a
port, we call it in-process, and build one LangChain tool per endpoint from its OpenAPI spec.
Tool names start with `oak_health_insurance_`, the same names CUGA's bundled Oak policies use.

Adapted from the CUGA Policy Playground Space (app/oak_tools.py), without per-visitor isolation.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional

import httpx
from langchain_core.tools import StructuredTool
from pydantic import Field, create_model

from oak_health import data as oak_data
from oak_health import main as oak_main

PREFIX = "oak_health_insurance_"
# Tables that change when the agent pays a bill or edits preferences.
MUTABLE_TABLES = ("PAYMENT_INTENTS", "BILLING_LEDGER", "MEMBER_PREFERENCES")
_SEED = {name: copy.deepcopy(getattr(oak_data, name)) for name in MUTABLE_TABLES}
NAMES = {"/plans": "list_plans", "/plans/compare": "compare_plans", "/plans/{plan_id}": "get_plan"}
_TYPES = {"string": str, "integer": int, "number": float, "boolean": bool}

# The member everyone plays (from Oak Bench). Pass it to every run as user context.
USER_CONTEXT = (
    "Member ID (string): 121231234\n"
    "Location: latitude(str):40.7128, longitude(str):-74.0060\n"
    "Current Date: 2025-12-31"
)


def reset_data() -> None:
    """Put bills, payments and preferences back to their starting values."""
    for name, seed in _SEED.items():
        table = getattr(oak_data, name)
        table.clear()
        table.update(copy.deepcopy(seed))


def bills() -> Dict[str, str]:
    """Current status of each bill, e.g. {'2025034AA2251': 'DUE 10.00'}."""
    from fastapi.testclient import TestClient

    items = TestClient(oak_main.app).post(
        "/get_member_billing", json={"memberId": "121231234"}, params={"size": 50}
    ).json()["items"]
    return {i["identifiers"]["displayId"]: f'{i["paymentStatus"]} {i["amountDue"]}' for i in items}


def _resolve(spec: dict, schema: dict) -> dict:
    while "$ref" in schema:
        schema = spec["components"]["schemas"][schema["$ref"].split("/")[-1]]
    return schema


def _py_type(spec: dict, schema: dict):
    schema = _resolve(spec, schema)
    for option in schema.get("anyOf", []):
        if option.get("type") != "null":
            return _py_type(spec, option)
    if schema.get("type") == "array":
        return List[_py_type(spec, schema.get("items", {}))]
    return _TYPES.get(schema.get("type"), Any)


def make_tools() -> List[StructuredTool]:
    """One tool per Oak Health endpoint, generated from the OpenAPI spec."""
    spec = oak_main.app.openapi()
    client = httpx.AsyncClient(transport=httpx.ASGITransport(app=oak_main.app), base_url="http://oak.local")
    tools = []
    for path, methods in spec["paths"].items():
        for method, op in methods.items():
            fields: Dict[str, Any] = {}
            where: Dict[str, str] = {}
            for p in op.get("parameters", []):
                py = _py_type(spec, p.get("schema", {}))
                if p.get("required"):
                    fields[p["name"]] = (py, Field(..., description=p.get("description") or ""))
                else:
                    fields[p["name"]] = (Optional[py], Field(p.get("schema", {}).get("default"), description=p.get("description") or ""))
                where[p["name"]] = p["in"]
            body = op.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema")
            if body:
                body = _resolve(spec, body)
                required = set(body.get("required", []))
                for name, prop in body.get("properties", {}).items():
                    py = _py_type(spec, prop)
                    desc = _resolve(spec, prop).get("description") or ""
                    fields[name] = (py, Field(..., description=desc)) if name in required else (Optional[py], Field(None, description=desc))
                    where[name] = "body"
            short = NAMES.get(path) or path.strip("/")

            async def call(_path=path, _method=method.upper(), _where=where, **kwargs):
                url, query, payload = _path, {}, {}
                for name, value in kwargs.items():
                    if value is None:
                        continue
                    if _where.get(name) == "path":
                        url = url.replace("{" + name + "}", str(value))
                    elif _where.get(name) == "query":
                        query[name] = value
                    else:
                        payload[name] = value
                response = await client.request(_method, url, params=query or None,
                                                json=payload if _method == "POST" else None, timeout=30)
                try:
                    return response.json()
                except ValueError:
                    return response.text

            tools.append(StructuredTool.from_function(
                coroutine=call, name=PREFIX + short,
                description=(op.get("description") or op.get("summary") or short).strip(),
                args_schema=create_model(f"{short}_args", **fields),
            ))
    return tools
