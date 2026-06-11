"""
Vignette 2 — Model Selection
Same prompt sent to claude-sonnet-4-6 (strong) and claude-haiku-4-5 (fast).
Prints answers side by side with latency and token comparison.
"""

import os
import time
from pathlib import Path
from dotenv import load_dotenv
from anthropic import AnthropicFoundry

load_dotenv()

client = AnthropicFoundry()
SONNET = os.getenv("CLAUDE_DEPLOYMENT_NAME", "claude-sonnet-4-6")
HAIKU  = "claude-haiku-4-5"

# Routing heuristic: short factual questions → haiku, deep analysis → sonnet
COMPLEX_KEYWORDS = {"explain", "compare", "design", "architect", "tradeoff", "difference"}

def route(question: str) -> str:
    return SONNET if any(kw in question.lower() for kw in COMPLEX_KEYWORDS) else HAIKU

def ask(model: str, question: str) -> tuple[str, float, int, int]:
    start = time.time()
    resp = client.messages.create(
        model=model,
        max_tokens=512,
        messages=[{"role": "user", "content": question}],
    )
    elapsed = time.time() - start
    return resp.content[0].text.strip(), elapsed, resp.usage.input_tokens, resp.usage.output_tokens

# Parse questions from eval set
raw = (Path(__file__).parent / "eval_set.txt").read_text()
questions = [line.split(": ", 1)[1] for line in raw.strip().splitlines() if line.startswith("QUESTION_")]

print("=" * 70)
print("MODEL COMPARISON — Sonnet 4.6 (strong) vs Haiku 4.5 (fast)")
print("=" * 70)

total = {"sonnet": {"tokens": 0, "time": 0.0}, "haiku": {"tokens": 0, "time": 0.0}}

for i, q in enumerate(questions, 1):
    routed = route(q)
    print(f"\n{'─' * 70}")
    print(f"Q{i}: {q}")
    print(f"   Routing hint → {routed}")
    print(f"{'─' * 70}")

    s_ans, s_time, s_in, s_out = ask(SONNET, q)
    h_ans, h_time, h_in, h_out = ask(HAIKU,  q)

    # Side-by-side (truncate to 300 chars for screen fit)
    print(f"\n[SONNET {s_time:.2f}s | {s_in+s_out} tok]")
    print(s_ans[:300] + ("…" if len(s_ans) > 300 else ""))
    print(f"\n[HAIKU  {h_time:.2f}s | {h_in+h_out} tok]")
    print(h_ans[:300] + ("…" if len(h_ans) > 300 else ""))

    total["sonnet"]["tokens"] += s_in + s_out
    total["sonnet"]["time"]   += s_time
    total["haiku"]["tokens"]  += h_in + h_out
    total["haiku"]["time"]    += h_time

print(f"\n{'=' * 70}")
print("SUMMARY")
print(f"{'=' * 70}")
print(f"{'Model':<12} {'Total tokens':>14} {'Total time':>12}")
print(f"{'─' * 40}")
print(f"{'Sonnet 4.6':<12} {total['sonnet']['tokens']:>14} {total['sonnet']['time']:>11.2f}s")
print(f"{'Haiku 4.5':<12} {total['haiku']['tokens']:>14}  {total['haiku']['time']:>10.2f}s")
speedup = total["sonnet"]["time"] / max(total["haiku"]["time"], 0.001)
print(f"\nHaiku was {speedup:.1f}x faster — use it for simple lookups, Sonnet for reasoning.")
print("=" * 70)
