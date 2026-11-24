"""Step 1: an Oak Health member assistant with no policies.

Run:  ./cuga-docker.sh python playground/step1_agent.py "Get all my 2025 approved claims"
"""

import asyncio
import sys

from agents import ask, make_agent, show


async def main(message: str) -> None:
    agent = await make_agent(with_policies=False)
    try:
        show(message, await ask(agent, message))
    finally:
        await agent.aclose()


if __name__ == "__main__":
    asyncio.run(main(" ".join(sys.argv[1:]) or "Get all my 2025 approved claims"))
