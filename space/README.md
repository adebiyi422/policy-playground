---
title: My Policy Playground
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
short_description: Two CUGA agents, with and without policies
---

# My Policy Playground

Two [CUGA](https://github.com/cuga-project/cuga-agent) agents answer the same message for the fictional
Oak Health Insurance. Same model, same tools; only the right one has policies (approvals, guards,
disclaimers and a playbook). Built by following the Policy Playground tutorial.

Set these in the Space's Settings: secrets `OPENAI_API_KEY` and `OPENAI_BASE_URL`, variable `MODEL_NAME`.
For IBM Bob inference, also add the variable `AGENT_SETTING_CONFIG=settings.bob.toml` and start the key with `Apikey `.
