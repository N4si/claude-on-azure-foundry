# Claude on Azure AI Foundry — Architecture Guide

A production-ready reference for how this project is structured,
how requests flow, and how to move from API keys to enterprise auth.

---

## System Architecture

```
                        ┌─────────────────────────────┐
                        │      Your Machine / CI       │
                        │                             │
                        │   ┌─────────────────────┐   │
                        │   │     Python App      │   │
                        │   │                     │   │
                        │   │  load_dotenv()      │   │
                        │   │  AnthropicFoundry() │   │
                        │   │  messages.create()  │   │
                        │   └────────┬────────────┘   │
                        │            │ HTTPS           │
                        └────────────┼────────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────────┐
                        │      Azure AI Foundry        │
                        │                             │
                        │  Resource: cloudchamp44-9277│
                        │  Region:   East US 2        │
                        │                             │
                        │  ┌─────────────────────┐   │
                        │  │  Authentication      │   │
                        │  │  API Key or Entra ID │   │
                        │  └────────┬────────────┘   │
                        │           │                 │
                        │  ┌────────▼────────────┐   │
                        │  │  Claude Deployment   │   │
                        │  │  claude-sonnet-4-6   │   │
                        │  │  claude-haiku-4-5    │   │
                        │  └────────┬────────────┘   │
                        └───────────┼─────────────────┘
                                    │
                                    ▼
                        ┌─────────────────────────────┐
                        │       Response               │
                        │                             │
                        │  content[0].text            │
                        │  usage.input_tokens         │
                        │  usage.output_tokens        │
                        │  model                      │
                        │  stop_reason                │
                        └─────────────────────────────┘
```

---

## Request Flow — Step by Step

```
Step 1   load_dotenv()
         Reads three environment variables from .env:
         ANTHROPIC_FOUNDRY_RESOURCE   → your resource name
         ANTHROPIC_FOUNDRY_API_KEY    → your API key
         CLAUDE_DEPLOYMENT_NAME       → claude-sonnet-4-6

Step 2   AnthropicFoundry()
         SDK builds the endpoint URL automatically:
         https://cloudchamp44-9277-resource.services.ai.azure.com/

Step 3   client.messages.create(model=deployment, messages=[...])
         Sends a POST request to Azure AI Foundry.
         Headers:  api-key, Content-Type: application/json
         Body:     model, max_tokens, system, messages

Step 4   Azure AI Foundry
         Authenticates the request.
         Routes to the correct Claude deployment.
         Applies guardrails and usage logging.

Step 5   Claude processes the request
         Reads the system prompt and user message.
         Generates a structured response.
         Returns content, usage, model, stop_reason.

Step 6   Your app receives the response
         response.content[0].text     → the answer
         response.usage.input_tokens  → billed input tokens
         response.usage.output_tokens → billed output tokens
```

---

## Authentication

### Local Development — API Key

The simplest path. Grab the key from the Foundry portal and put it in .env.
The SDK reads it automatically — nothing is hardcoded.

```
.env
────────────────────────────────────────────────────
ANTHROPIC_FOUNDRY_RESOURCE=cloudchamp44-9277-resource
ANTHROPIC_FOUNDRY_API_KEY=your-key-here
CLAUDE_DEPLOYMENT_NAME=claude-sonnet-4-6
────────────────────────────────────────────────────

app.py
────────────────────────────────────────────────────
from anthropic import AnthropicFoundry
from dotenv import load_dotenv

load_dotenv()
client = AnthropicFoundry()   # reads env vars — no secrets in code
────────────────────────────────────────────────────
```

### Production — Azure Entra ID (Recommended)

No API key. No secret rotation. Identity-based access via Azure RBAC.
Works automatically on Azure VMs, AKS, GitHub Actions, and local az login.

```python
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from anthropic import AnthropicFoundry

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default",
)

client = AnthropicFoundry(azure_ad_token_provider=token_provider)
```

Why Entra ID in production:
- No long-lived secrets anywhere in your codebase
- Tokens expire automatically — nothing to rotate manually
- Azure RBAC controls who can call the model
- Full audit trail in Azure Monitor

---

## The AnthropicFoundry Client

AnthropicFoundry is a thin Azure-native wrapper around the standard Anthropic SDK.
The interface is identical — only the setup differs.

```
                    Standard API          Azure AI Foundry
                    ──────────────────    ──────────────────────────
Import              from anthropic        from anthropic
                    import Anthropic      import AnthropicFoundry

Init                Anthropic()           AnthropicFoundry()

Auth                ANTHROPIC_API_KEY     ANTHROPIC_FOUNDRY_API_KEY
                                          or Entra ID token provider

Endpoint            api.anthropic.com     your-resource.services
                                          .ai.azure.com

Methods             messages.create()     messages.create()
                    messages.stream()     messages.stream()
                    (identical)           (identical)
```

Every method works identically once the client is initialized.
Switching from direct API to Foundry is a two-line change.

---

## Usage Object — Monitoring and Cost Tracking

Every response includes a usage object. Log it. Every call.

```python
response = client.messages.create(...)

# Cost tracking
print(f"Input tokens  : {response.usage.input_tokens}")
print(f"Output tokens : {response.usage.output_tokens}")
print(f"Model         : {response.model}")
print(f"Stop reason   : {response.stop_reason}")
```

Use this for:

  Cost visibility       Each token has a price. Input and output are billed
                        at different rates. Log both.

  Reproducibility       Same input + same model = same token count.
                        Use this to verify your workflow is stable.

  Capacity planning     claude-sonnet-4-6 supports 200K input tokens.
                        Track how close your prompts are to the limit.

  Debugging             stop_reason tells you if the model finished normally
                        (end_turn) or hit the token limit (max_tokens).

---

## Key Design Decisions

  Start simple           This project uses no orchestration framework,
                         no vector database, no Docker. One Python file
                         per vignette. That makes the workflow easy to
                         understand, easy to demo, and easy to extend.

  File-based input       Each script reads its input from a .txt file.
                         In production this would be a webhook, a queue
                         message, or a database record. The AI logic
                         is identical either way.

  One .env for all       A single .env at the root works for all five
                         vignettes. One resource, one key, one model.

  API key first          Start with API key auth locally. Swap to Entra
                         ID before any real users or real data are involved.
                         The code change is two lines.

---

## Project Structure

```
claude-on-azure-foundry/
│
├── .env                    # your credentials (never committed)
├── .env.example            # template for new contributors
├── requirements.txt        # anthropic, python-dotenv, pytest
│
├── quickstart/             # Vignette 1 — simplest possible API call
│   ├── app.py
│   └── ci_failure.txt
│
├── model-selection/        # Vignette 2 — same prompt, two models
│   ├── compare.py
│   └── eval_set.txt
│
├── debugging/              # Vignette 3 — find and fix bugs with Claude
│   ├── analyze.py
│   ├── buggy_code.py
│   └── test_buggy.py
│
├── incident-response/      # Vignette 4 — production incident triage
│   ├── analyze.py
│   └── incident_logs.txt
│
└── docs/
    └── architecture.md     # Vignette 5 — this file
```