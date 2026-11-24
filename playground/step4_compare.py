"""Step 4: the playground. Send the same message to both agents and count the broken rules.

The agent without policies runs first, then the data is reset and the agent with policies runs.
When the agent with policies pauses for approval, this script approves (like a member clicking "Approve").

Run:  ./cuga-docker.sh python playground/step4_compare.py            # all scenarios
      ./cuga-docker.sh python playground/step4_compare.py chest_pain # one scenario
"""

import asyncio
import sys

from agents import answer_approval, ask, make_agent
from oak_tools import bills, reset_data
from scenarios import SCENARIOS, check_rules


async def run_side(agent, message: str) -> dict:
    reset_data()
    out = await ask(agent, message)
    out["approvals"] = 0
    while out["paused"] and out["approvals"] < 5:
        out["approvals"] += 1
        tools_so_far = out["tools"]
        out = {**await answer_approval(agent, out["thread_id"], approve=True), "approvals": out["approvals"]}
        out["tools"] = tools_so_far + out["tools"]
    out["bills"] = bills()
    return out


def column(title: str, out: dict, broken: list) -> str:
    lines = [f"--- {title} ---", f"tools: {', '.join(out['tools']) or 'none'}"]
    if out["approvals"]:
        lines.append(f"asked for approval {out['approvals']} time(s)")
    lines.append("RULES BROKEN: " + ("; ".join(broken) if broken else "none"))
    lines.append(out["answer"].strip()[:700])
    return "\n".join(lines)


async def main(only: list) -> None:
    without = await make_agent(with_policies=False)
    with_p = await make_agent(with_policies=True)
    totals = {"without": 0, "with": 0}
    try:
        for sc in SCENARIOS:
            if only and sc["id"] not in only:
                continue
            print(f"\n================ {sc['label']} :: \"{sc['message']}\" ================")
            for name, agent in (("without", without), ("with", with_p)):
                out = await run_side(agent, sc["message"])
                broken = check_rules(sc, out)
                totals[name] += len(broken)
                print(column(f"{name.upper()} policies", out, broken))
        print(f"\nTOTAL RULES BROKEN  without policies: {totals['without']}   with policies: {totals['with']}")
    finally:
        await without.aclose()
        await with_p.aclose()


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
