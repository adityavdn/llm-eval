"""Runs every question in questions.json through several LLMs on Groq and scores the answers.
Stdlib only.   GROQ_API_KEY=... python3 run_eval.py        (optional: MODELS=a,b,c)

Scoring is deterministic (exact match, number match, format checks), with no
"LLM as judge", so the results are reproducible and can't be gamed by a judge's bias.
"""
import datetime as dt
import json
import os
import re
import time
import urllib.error
import urllib.request

API = os.environ.get("LLM_API", "https://api.groq.com/openai/v1")   # any OpenAI-compatible API works
SYSTEM = ("Answer with only the final answer, no explanation. "
          "If a question is based on something false, or you don't know, reply exactly: I don't know")
# Tried in this order; whichever Groq currently offers are used (max 5).
PREFERRED = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "openai/gpt-oss-20b", "openai/gpt-oss-120b",
             "qwen/qwen3-32b", "meta-llama/llama-4-scout-17b-16e-instruct", "moonshotai/kimi-k2-instruct",
             "gemma2-9b-it", "mistral-saba-24b"]
SKIP = re.compile(r"whisper|tts|guard|embed|playai|orpheus|prompt-guard|compound", re.I)
REFUSAL = re.compile(r"(don'?t|do not|can'?t|cannot) know|not aware|doesn'?t exist|does not exist|no such|fictional|"
                     r"not a real|never (won|existed|happened|adopted|received|gave)|no (record|information|evidence)|"
                     r"there (is|was|are|were) no|has(n'?t| not) (been|walked|discovered)|no one has|nobody has|"
                     r"hypothetical|not been discovered|unknown|did not|didn'?t", re.I)


def call(path, body=None):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body else None, headers={
        "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}", "Content-Type": "application/json",
        "User-Agent": "llm-eval"})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 5:                       # rate limited: wait and retry
                time.sleep(float(e.headers.get("retry-after") or 10))
                continue
            raise


def pick_models():
    if os.environ.get("MODELS"):
        return os.environ["MODELS"].split(",")
    available = [m["id"] for m in call("/models")["data"] if not SKIP.search(m["id"])]
    chosen = [m for m in PREFERRED if m in available]
    return (chosen or sorted(available))[:5]


def clean(text):
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S)      # reasoning models' scratchpad
    return text.strip()


def norm(s):
    s = s.lower().strip().strip("`'\"").strip()
    s = re.sub(r"^(the )?(final )?answer( is)?:?\s*", "", s)
    return re.sub(r"\s+", " ", s).rstrip(".!").strip()


def first_number(s):
    m = re.search(r"-?\d+(\.\d+)?", s.replace(",", ""))
    return float(m.group()) if m else None


def score(q, answer):
    """True if the answer passes this question's check."""
    a, want, check = answer.strip(), q["answer"], q["check"]
    if check == "refuse":
        return bool(REFUSAL.search(a))
    if check == "number":
        n = first_number(a)
        return n is not None and abs(n - float(want)) < 1e-6
    if check == "contains":
        return want in a.lower()
    if check == "exact":
        return norm(a) == want
    if check == "exact_case":
        return a.strip("`'\" .\n") == want
    if check == "words":
        return len(re.findall(r"[A-Za-z][A-Za-z'-]*", a)) == int(want)
    if check == "range":
        lo, hi = map(int, want.split("-"))
        return re.fullmatch(r"\d+", a.strip(" .")) is not None and lo <= int(a.strip(" .")) <= hi
    if check == "no_letter":
        return want not in a.lower() and len(a.split()) >= 5
    if check == "json":
        try:
            got = json.loads(re.sub(r"^```(json)?|```$", "", a.strip(), flags=re.M).strip())
        except ValueError:
            return False
        return got == json.loads(want)
    raise ValueError(f"unknown check {check}")


def ask(model, prompt):
    start = time.time()
    r = call("/chat/completions", {"model": model, "temperature": 0, "max_tokens": 1024, "messages": [
        {"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}]})
    return clean(r["choices"][0]["message"].get("content")), round((time.time() - start) * 1000), \
        r.get("usage", {}).get("completion_tokens", 0)


if __name__ == "__main__":
    questions = json.load(open("questions.json"))
    models = pick_models()
    print("Models:", ", ".join(models))
    results = []
    for model in models:
        passed = 0
        for q in questions:
            try:
                answer, ms, tokens = ask(model, q["prompt"])
                error = None
            except Exception as e:                          # one broken model shouldn't kill the run
                answer, ms, tokens, error = "", None, 0, str(e)[:200]
            ok = score(q, answer)
            passed += ok
            results.append({"model": model, "qid": q["id"], "answer": answer[:500], "pass": ok,
                            "latency_ms": ms, "tokens": tokens, "error": error})
            time.sleep(float(os.environ.get("DELAY", 1.5)))                               # stay under the free tier's rate limit
        print(f"  {model}: {passed}/{len(questions)}")
    json.dump({"run_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes"), "system_prompt": SYSTEM,
               "models": models, "questions": questions, "results": results},
              open("results.json", "w"), indent=1)
    print("Saved results.json")
