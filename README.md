# Claude on Azure AI Foundry

[![Azure AI Foundry](https://img.shields.io/badge/Azure%20AI-Foundry-0078D4?logo=microsoftazure&logoColor=white)](https://ai.azure.com)
[![Claude](https://img.shields.io/badge/Claude-Sonnet%204.6-D97706?logo=anthropic&logoColor=white)](https://anthropic.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Microsoft Azure AI Skills Fest** · Sponsored content for [CloudChamp](https://youtube.com/@cloudchamp)

Run Claude on your own Azure infrastructure — same API, enterprise security, no data leaves your tenant.

---

## How it works

```
┌──────────────┐     HTTPS      ┌─────────────────────────┐     API      ┌─────────────┐
│  Python App  │ ─────────────► │   Azure AI Foundry      │ ───────────► │   Claude    │
│  (local/CI)  │                │   Your Azure Tenant     │              │  Sonnet 4.6 │
│              │ ◄───────────── │   East US 2             │ ◄─────────── │             │
└──────────────┘    Response    └─────────────────────────┘   Response   └─────────────┘
        │                                   │
        │ load_dotenv()            API Key (dev) · Entra ID (prod)
        ▼
   .env file
```

| Environment | Auth method |
|---|---|
| Development | API Key — `ANTHROPIC_FOUNDRY_API_KEY` in `.env` |
| Production | Entra ID managed identity — no secrets stored |

---

## Demo vignettes

| # | Folder | What it shows |
|---|---|---|
| 1 | [`quickstart/`](quickstart/) | Simplest Claude API call — CI failure analysis |
| 2 | [`model-selection/`](model-selection/) | Sonnet vs Haiku — latency, cost, routing logic |
| 3 | [`debugging/`](debugging/) | Paste a bug → root cause + fix → tests pass |
| 4 | [`incident-response/`](incident-response/) | K8s prod incident → structured triage report |
| 5 | [`docs/architecture.md`](docs/architecture.md) | Auth walkthrough — API key → Entra ID |

---

## Quick start

**Prerequisites:** Python 3.10+, Azure AI Foundry resource with Claude deployed

```bash
# 1. Clone
git clone https://github.com/n4si/claude-on-azure-foundry.git
cd claude-on-azure-foundry

# 2. Install
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env — add your Foundry resource name and API key

# 4. Run
python quickstart/app.py
```

---

## Environment variables

```bash
# .env — never commit this file
ANTHROPIC_FOUNDRY_RESOURCE=your-resource-name
ANTHROPIC_FOUNDRY_API_KEY=your-api-key-here
CLAUDE_DEPLOYMENT_NAME=claude-sonnet-4-6
```

Find these in the Foundry portal under your deployment → **Details**.

---

## Running each demo

```bash
# Vignette 1 — CI failure analysis
python quickstart/app.py

# Vignette 2 — model comparison (Sonnet vs Haiku)
python model-selection/compare.py

# Vignette 3 — AI debugging
pytest debugging/ -v                # see the failures first
python debugging/analyze.py         # Claude finds and fixes them

# Vignette 4 — incident triage
python incident-response/analyze.py
```

---

## Project structure

```
claude-on-azure-foundry/
├── README.md
├── requirements.txt              # anthropic, python-dotenv, pytest
├── .env.example                  # copy to .env and fill in values
├── .gitignore
│
├── quickstart/
│   ├── app.py                    # 45-line Claude API call
│   └── ci_failure.txt            # sample CI failure log
│
├── model-selection/
│   ├── compare.py                # Sonnet vs Haiku side-by-side
│   └── eval_set.txt              # 5 engineering questions
│
├── debugging/
│   ├── analyze.py                # AI root cause + auto-fix
│   ├── buggy_code.py             # 3 intentional bugs
│   └── test_buggy.py             # pytest suite (3 failing → 6 passing)
│
├── incident-response/
│   ├── analyze.py                # structured SRE triage report
│   └── incident_logs.txt         # realistic K8s P0 incident
│
└── docs/
    └── architecture.md           # auth flow + system design
```

---

## Why Azure AI Foundry

- **Data sovereignty** — your traffic stays in your Azure tenant
- **Enterprise auth** — Entra ID managed identity, no API keys in production
- **Same SDK** — `AnthropicFoundry()` is a drop-in for `Anthropic()`
- **Usage visibility** — every response includes input/output token counts

---

*Built for the Microsoft Azure AI Skills Fest content series.*