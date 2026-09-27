# LLM Evaluation

**Live results:** https://adityavdn.github.io/llm-eval/

A reproducible benchmark that compares open-source large language models on the same 50 questions,
then publishes an interactive leaderboard.

| Category | What it tests |
|---|---|
| Maths | Multi-step word problems |
| Knowledge | Facts with one correct answer |
| Reasoning | Classic trick questions (bat & ball, letters in "strawberry") |
| Instructions | Exact output formats: word counts, JSON, capitals, banned letters |
| Hallucination traps | Questions about things that don't exist. A model passes only if it refuses to make something up |

**Method**
- Every model gets the same system prompt, temperature 0, and the same 50 questions (`questions.json`).
- **Deterministic scoring, with no "LLM-as-a-judge".** Each question has a rule-based check (number match, exact
  match, format validation, refusal detection), so results are reproducible and free of judge bias. The checks are
  tested in `test_eval.py`.
- It measures accuracy per category, latency, and output length.
- Models run on the Groq API (free tier). Any OpenAI-compatible API also works: set `LLM_API`.

**Run it**
```bash
GROQ_API_KEY=... python3 run_eval.py          # writes results.json
python3 -m http.server                        # open http://localhost:8000
```
Or run it from the **Actions** tab ("Run evaluation") and the site updates itself.

**Limitations:** 50 questions is a small sample (each question is worth 2%), and rule-based checks can
occasionally mark a correct answer wrong if it's phrased unusually. Every answer is shown on the site so you can check.
