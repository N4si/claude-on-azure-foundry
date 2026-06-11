"""
Vignette 4 — Incident Response
Reads production K8s incident logs and generates a structured triage report.
"""

import os
import textwrap
from pathlib import Path
from dotenv import load_dotenv
from anthropic import AnthropicFoundry

load_dotenv()

client     = AnthropicFoundry()
deployment = os.getenv("CLAUDE_DEPLOYMENT_NAME", "claude-sonnet-4-6")

logs = (Path(__file__).parent / "incident_logs.txt").read_text()

SYSTEM = """You are a senior site reliability engineer on call for a P0 production incident.
Analyze the logs and produce a triage report with exactly these five sections.

IMPORTANT FORMATTING RULES:
- Plain text only. No markdown. No backticks. No ** bold **. No # headers.
- Write code and commands on their own line with 4 spaces of indentation.
- Use the emoji section headers exactly as shown below.
- Separate each section with a blank line.
- Keep each line under 90 characters. Do not let lines run long.
- Be concise and direct. Every line should be actionable.

🔴 EXECUTIVE SUMMARY
Two sentences max: what broke and what the user impact was.

🔍 ROOT CAUSE ANALYSIS
Numbered list of causes, most likely first.
Include the deployment or config change that triggered it.

⚡ IMMEDIATE ACTIONS
Numbered steps to stop the bleeding RIGHT NOW.
Each step must include the exact command indented with 4 spaces.

🛠️  KUBECTL COMMANDS
Copy-paste ready commands for checking pod status, tailing logs, restarting safely.
Label each command with what it does.

✅ VALIDATION STEPS
How to confirm the system is stable before declaring the incident resolved.
Include the exact command and expected output for each check.
"""

print()
print("┌─────────────────────────────────────────────────────────┐")
print("│       PRODUCTION INCIDENT TRIAGE — Azure AI Foundry     │")
print("│                   Powered by Claude                      │")
print("└─────────────────────────────────────────────────────────┘")
print()
print(f"  Model      : {deployment}")
print(f"  Input file : incident_logs.txt")
print(f"  Severity   : P0 — Production Down")
print()
print("  Analyzing incident with Claude...")
print()

response = client.messages.create(
    model=deployment,
    max_tokens=2048,
    system=SYSTEM,
    messages=[
        {"role": "user", "content": f"Production incident logs:\n\n{logs}"}
    ],
)

print("─" * 60)
for line in response.content[0].text.splitlines():
    if line.strip() == "":
        print()
    elif line.startswith("    "):
        # preserve indented commands exactly
        print(line)
    else:
        print(textwrap.fill(line, width=90, subsequent_indent="  "))
print("─" * 60)
print()
print("  📊 USAGE — monitoring & cost tracking")
print(f"     Model         : {response.model}")
print(f"     Input tokens  : {response.usage.input_tokens}")
print(f"     Output tokens : {response.usage.output_tokens}")
print(f"     Stop reason   : {response.stop_reason}")
print()