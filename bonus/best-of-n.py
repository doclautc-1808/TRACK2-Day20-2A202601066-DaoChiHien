#!/usr/bin/env python3
"""C4: compare one generation with four parallel candidates + a tiny reranker."""
from __future__ import annotations

import concurrent.futures
import json
import pathlib
import re
import sys
import time

import httpx

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "lib"))
import labkit  # noqa: E402

PROMPT = (
    "Explain why goodput@SLO is more useful than raw throughput for an LLM "
    "serving team. Answer in exactly two concise sentences."
)


def generate(base: str, seed: int) -> dict:
    body = {
        "model": "local",
        "messages": [{"role": "user", "content": PROMPT}],
        "max_tokens": 24,
        "temperature": 0.8,
        "seed": seed,
    }
    start = time.perf_counter()
    response = httpx.post(f"{base}/v1/chat/completions", json=body, timeout=420.0)
    response.raise_for_status()
    text = response.json()["choices"][0]["message"]["content"].strip()
    latency_ms = (time.perf_counter() - start) * 1000
    words = re.findall(r"\b\w+\b", text.lower())
    sentences = len(re.findall(r"[.!?](?:\s|$)", text))
    score = (
        2 * ("goodput" in words)
        + 2 * ("slo" in words or "latency" in words)
        + 2 * (sentences == 2)
        + 1 * ("throughput" in words)
        - 0.05 * max(0, len(words) - 55)
    )
    return {
        "seed": seed,
        "latency_ms": round(latency_ms, 1),
        "sentences": sentences,
        "words": len(words),
        "score": round(score, 2),
        "text": text,
    }


def main() -> int:
    base = f"http://127.0.0.1:{labkit.server_port()}"
    labkit.banner("C4 - Best-of-N with heuristic reranking")
    print(f"  endpoint: {base} · N=4 · --parallel 4 expected")

    single = generate(base, 100)
    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        candidates = list(pool.map(lambda seed: generate(base, seed), range(101, 105)))
    best_of_n_ms = (time.perf_counter() - start) * 1000
    best = max(candidates, key=lambda item: item["score"])

    rows = [["single", single["seed"], single["latency_ms"], single["sentences"],
             single["words"], single["score"]]]
    rows.extend([[f"candidate {i}", c["seed"], c["latency_ms"], c["sentences"],
                  c["words"], c["score"]] for i, c in enumerate(candidates, 1)])
    table = labkit.md_table(
        ["Mode", "Seed", "Latency (ms)", "Sentences", "Words", "Heuristic score"], rows
    )
    latency_ratio = best_of_n_ms / single["latency_ms"] if single["latency_ms"] else 0.0
    md = f"""# Bonus C4 - Best-of-N with reranking

Host `{labkit.host_tag()}` · llama.cpp `{labkit.LLAMA_CPP_BUILD}` · N=4 parallel
candidates · temperature 0.8 · output budget 24 tokens

Prompt: *{PROMPT}*

{table}

Single-shot wall latency: **{single['latency_ms']:.1f} ms**

Best-of-4 wall latency: **{best_of_n_ms:.1f} ms** ({latency_ratio:.2f}x single-shot)

Chosen candidate: seed **{best['seed']}**, heuristic score **{best['score']:.2f}**

## Single-shot answer

> {single['text']}

## Selected Best-of-4 answer

> {best['text']}

## Finding

Best-of-N uses the four decode slots for one user instead of four users. Compare the
single and selected scores above: a latency increase is only justified when reranking
actually improves the measured quality signal. The heuristic checks structure and
keywords, not factual correctness, so its score must not be presented as an accuracy
metric.
"""
    out = labkit.write_report("bonus-c4-best-of-n.md", md, {
        "prompt": PROMPT,
        "single": single,
        "candidates": candidates,
        "selected_seed": best["seed"],
        "best_of_n_wall_ms": round(best_of_n_ms, 1),
    })
    print(md)
    print(f"==> Wrote {out.relative_to(labkit.repo_root())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
