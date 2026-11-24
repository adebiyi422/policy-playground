"""Step 3: approval before a payment, and the denied-claim playbook.

Run:  ./cuga-docker.sh python playground/step3_approval.py --decline
      ./cuga-docker.sh python playground/step3_approval.py --approve
      ./cuga-docker.sh python playground/step3_approval.py --approve "Pay everything I owe."
"""

import asyncio
import sys

from agents import answer_approval, ask, make_agent, show
from oak_tools import bills, reset_data

MAX_APPROVALS = 5  # "Pay everything" can ask once per bill


async def main(approve: bool, message: str) -> None:
    reset_data()
    print("Bills before:", bills())
    agent = await make_agent(with_policies=True)
    try:
        out = await ask(agent, message)
        show(message, out)
        for _ in range(MAX_APPROVALS):
            if not out["paused"]:
                break
            print(f"\n>>> The member {'APPROVES' if approve else 'DECLINES'} the held action")
            out = await answer_approval(agent, out["thread_id"], approve)
            show("after the decision", out)
        print("\nBills after:", bills())
    finally:
        await agent.aclose()


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    asyncio.run(main("--approve" in sys.argv, " ".join(args) or "Pay the due payment for 2025034AA2251 claim id."))
