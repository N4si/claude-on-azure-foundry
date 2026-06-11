import os
from pathlib import Path
from dotenv import load_dotenv
from anthropic import AnthropicFoundry

load_dotenv()

client = AnthropicFoundry()  # reads ANTHROPIC_FOUNDRY_RESOURCE + ANTHROPIC_FOUNDRY_API_KEY
deployment = os.getenv("CLAUDE_DEPLOYMENT_NAME", "claude-sonnet-4-6")

# Load the CI failure log
failure_log = Path(__file__).parent / "ci_failure.txt"
error_text = failure_log.read_text()

print()
print("┌─────────────────────────────────────────────────────────┐")
print("│         CI FAILURE ANALYZER — Azure AI Foundry          │")
print("│                  Powered by Claude                       │")
print("└─────────────────────────────────────────────────────────┘")
print()
print(f"  Model      : {deployment}")
print(f"  Input file : ci_failure.txt")
print()
print("  Analyzing failure with Claude...")
print()

response = client.messages.create(
    model=deployment,
    max_tokens=1024,
    system=(
        "You are a senior software engineer doing code review. "
        "When given a CI failure, respond with exactly three sections:\n\n"
        "🔴 WHAT FAILED\n"
        "One clear sentence explaining the root cause.\n\n"
        "🔧 EXACT FIX\n"
        "The minimal code change needed, with file path and line number.\n\n"
        "✅ HOW TO VERIFY\n"
        "One command to confirm the fix works."
    ),
    messages=[
        {"role": "user", "content": f"CI failure log:\n\n{error_text}"}
    ],
)

print("─" * 60)
print(response.content[0].text)
print("─" * 60)
print()
print("  📊 USAGE — monitoring & cost tracking")
print(f"     Model         : {response.model}")
print(f"     Input tokens  : {response.usage.input_tokens}")
print(f"     Output tokens : {response.usage.output_tokens}")
print(f"     Stop reason   : {response.stop_reason}")
print()