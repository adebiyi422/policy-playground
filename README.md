# Policy Playground starter folder

The files for the CUGA Policy Playground tutorial: two [CUGA](https://github.com/cuga-project/cuga-agent)
assistants for the fictional Oak Health Insurance, one without policies and one with seven.

| Path | What it is |
|---|---|
| `pyproject.toml`, `uv.lock`, `.python-version` | Which packages to install (`cuga`, `cuga-oak-health`) |
| `Dockerfile`, `cuga-docker.sh` | The container, and a script that runs commands in it |
| `llm_smoke.py` | Checks that your model key works |
| `.env` | Your model settings. You create it, and git and Docker ignore it |
| `playground/` | The assistants, the policies and the web page |
| `space/` | The two files for a Hugging Face Space (Part 5) |

Start with Part 1 of the tutorial: [`docs/policy-playground-tutorial.html`](docs/policy-playground-tutorial.html). Download it and open it in a browser, or view it at [this page](https://htmlpreview.github.io/?https://github.com/adebiyi422/policy-playground/blob/main/docs/policy-playground-tutorial.html). Every command runs through `./cuga-docker.sh`, for example:

```bash
./cuga-docker.sh python llm_smoke.py
```

Never commit `.env`. On Hugging Face, the Space's secrets replace it.
