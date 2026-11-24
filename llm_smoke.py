"""LLM readiness check (from the using-cuga skill).

Run with: ./cuga-docker.sh python llm_smoke.py
"""

import asyncio
import os
from pathlib import Path

from cuga.backend.llm.load_test_mock import is_mock_llm_enabled
from cuga.backend.llm.models import LLMManager
from cuga.config import settings
import cuga.config as cuga_config


async def main():
    if is_mock_llm_enabled():
        raise RuntimeError("Mock LLM mode cannot verify provider readiness")

    print("AGENT_SETTING_CONFIG:", os.getenv("AGENT_SETTING_CONFIG"))
    print("MODEL_NAME:", os.getenv("MODEL_NAME"))
    print("tracker_enabled:", settings.advanced_features.tracker_enabled)
    traj = Path(cuga_config.TRAJECTORY_DATA_DIR)
    traj.mkdir(parents=True, exist_ok=True)
    print("TRAJECTORY_DATA_DIR:", traj.resolve(), "writable:", os.access(traj, os.W_OK))

    model = LLMManager().get_model(settings.agent.code.model)
    reply = await model.ainvoke("Reply with a short greeting.")
    if not reply.content:
        raise RuntimeError("The configured LLM returned no content")
    print("Configured LLM request succeeded")


asyncio.run(main())
