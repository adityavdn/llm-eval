import json
from run_eval import score, clean

Q = {q["id"]: q for q in json.load(open("questions.json"))}
good = {"m1": "72 km/h", "m2": "£34.00", "m9": "Wednesday.", "f2": "Au", "f3": "Jane Austen", "r2": "Yes",
        "r9": "a", "r10": "nohtyp", "i1": "Vast, blue, restless.", "i2": "BANANA", "i3": "2,3,5,7,11",
        "i4": '```json\n{"name": "Sam", "age": 30}\n```', "i6": "A cat naps on a warm rug.", "i7": "7",
        "i9": "TAC", "i10": "Four.", "h1": "I don't know", "h7": "The UK never adopted the euro.",
        "h8": "No one has walked on Mars yet.", "r3": "5p"}
bad = {"m1": "80", "f2": "Ag", "r2": "No", "r9": "t", "i1": "The sea is vast", "i2": "banana",
       "i3": "2, 3, 5, 7, 11", "i4": '{"name": "Sam", "age": "30"}', "i6": "The cat sleeps on the mat here.",
       "i7": "11", "i9": "tac", "i10": "4", "h1": "Geoffrey Hinton won it.", "h3": "A mapmaker in 1890s Cardiff...",
       "r3": "10p"}
for qid, a in good.items():
    assert score(Q[qid], a), ("should pass", qid, a)
for qid, a in bad.items():
    assert not score(Q[qid], a), ("should fail", qid, a)
assert clean("<think>hmm 2+2</think>\nfour") == "four"
print("ok", len(good) + len(bad), "scoring checks")
