# LLM Evaluation

A reproducible benchmark for comparing open-source language models on the same evaluation set and publishing an interactive leaderboard.

## Overview

This project evaluates large language models on a shared set of prompts and scores them using deterministic rules instead of an LLM-as-a-judge approach. The goal is to make model comparisons transparent, reproducible and easy to inspect.

## Evaluation categories

The benchmark includes questions across:

- mathematics
- factual recall
- reasoning
- instruction following
- hallucination traps

## Method

- Each model receives the same system prompt and evaluation questions.
- Output is scored using rule-based checks.
- Metrics include category accuracy, latency and output length.
- Results are presented in a browser-based leaderboard.

## Tech Stack

- Python
- JavaScript
- HTML
- Groq API
- OpenAI-compatible APIs

## How to run

```bash
GROQ_API_KEY=... python3 run_eval.py
python3 -m http.server
```

Then open the local site in a browser.

## Project structure

```text
.
├── run_eval.py
├── questions.json
├── test_eval.py
├── index.html or dashboard files
├── README.md
└── results output files
```

