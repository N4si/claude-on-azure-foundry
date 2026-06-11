"""
Vignette 3 — AI-Powered Debugging
Runs the test suite, captures failures, sends them to Claude,
gets root cause + fix, applies the fix, re-runs tests.
"""

import os
import re
import textwrap
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from anthropic import AnthropicFoundry

load_dotenv()

client     = AnthropicFoundry()
deployment = os.getenv("CLAUDE_DEPLOYMENT_NAME", "claude-sonnet-4-6")
here       = Path(__file__).parent

def run_tests() -> tuple[bool, str]:
    result = subprocess.run(
        ["python", "-m", "pytest", str(here), "-v", "--tb=short"],
        capture_output=True, text=True, cwd=here,
    )
    passed = result.returncode == 0
    return passed, result.stdout + result.stderr

def ask_claude(source: str, test_output: str) -> str:
    resp = client.messages.create(
        model=deployment,
        max_tokens=2048,
        system=(
            "You are a senior Python engineer doing code review. "
            "When given buggy source code and failing test output, respond with "
            "plain text only — no markdown, no backticks, no ** bold **.\n\n"
            "Use exactly these three section headers:\n"
            "🔍 LIKELY CAUSES\n"
            "Numbered list of root causes. One sentence each. Max 90 chars per line.\n\n"
            "🔧 SMALLEST FIX\n"
            "The corrected Python source as plain text, indented with 4 spaces. "
            "Full file, no omissions. Max 90 chars per line.\n\n"
            "✅ VALIDATION\n"
            "One pytest command to confirm the fix works."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Source file (buggy_code.py):\n{source}\n\n"
                f"Failing test output:\n{test_output}"
            ),
        }],
    )
    return resp.content[0].text, resp.usage

def print_wrapped(text: str) -> None:
    for line in text.splitlines():
        if line.strip() == "":
            print()
        elif line.startswith("    "):
            print(line)
        else:
            print(textwrap.fill(line, width=90, subsequent_indent="  "))

print()
print("┌─────────────────────────────────────────────────────────┐")
print("│          AI-POWERED DEBUGGING — Azure AI Foundry        │")
print("│                   Powered by Claude                      │")
print("└─────────────────────────────────────────────────────────┘")
print()
print(f"  Model      : {deployment}")
print(f"  Input file : buggy_code.py")
print()

# Step 1: run tests to see failures
passed, test_output = run_tests()

if passed:
    print("  ✅ All tests already pass — nothing to fix.")
else:
    print("  ❌ Tests failed. Sending to Claude for analysis...")
    print()
    source = (here / "buggy_code.py").read_text()

    # Step 2: ask Claude
    analysis, usage = ask_claude(source, test_output)

    print("─" * 60)
    print_wrapped(analysis)
    print("─" * 60)

    # Step 3: extract fixed source and apply it
    # Claude returns plain indented code — extract between 🔧 and ✅
    match = re.search(
        r"🔧 SMALLEST FIX\n(.*?)(?=✅ VALIDATION|$)", analysis, re.DOTALL
    )
    if match:
        raw = match.group(1).strip()
        # remove 4-space indentation Claude added
        fixed_source = "\n".join(
            line[4:] if line.startswith("    ") else line
            for line in raw.splitlines()
        )
        (here / "buggy_code.py").write_text(fixed_source)
        print()
        print("  🔨 Fix applied. Re-running tests...")
        print()
        passed2, output2 = run_tests()
        print(output2)
        if passed2:
            print("  ✅ All tests passing after fix.")
        else:
            print("  ❌ Tests still failing — apply the fix above manually.")
    else:
        print()
        print("  ⚠️  Could not extract code — apply the fix above manually.")

    print()
    print("  📊 USAGE — monitoring & cost tracking")
    print(f"     Model         : {deployment}")
    print(f"     Input tokens  : {usage.input_tokens}")
    print(f"     Output tokens : {usage.output_tokens}")
    print()