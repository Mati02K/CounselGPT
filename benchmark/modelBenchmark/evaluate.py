import json, requests
from sentence_transformers import SentenceTransformer, util

API_URL = "https://counselgpt-mathesh.nrp-nautilus.io/infer"

# Load evaluation data
questions = json.load(open("questions.json"))
gold = json.load(open("answers.json"))

model = SentenceTransformer("all-mpnet-base-v2")

# Final output structure
results = {}

def similarity(a, b):
    emb1 = model.encode(a, convert_to_tensor=True)
    emb2 = model.encode(b, convert_to_tensor=True)
    return float(util.cos_sim(emb1, emb2))

for q in questions:
    # ---- Query QWEN ----
    r_qwen = requests.post(API_URL, json={
        "prompt": q,
        "max_tokens": 200,
        "model_name": "qwen",
        "use_cache": False
    }).json()

    qwen_ans = r_qwen["response"]

    # ---- Query LLAMA ----
    r_base = requests.post(API_URL, json={
        "prompt": q,
        "max_tokens": 200,
        "model_name": "base",
        "use_cache": False
    }).json()

    base_ans = r_base["response"]

    # ---- Score against gold ----
    gold_ans = gold[q]

    qwen_score = similarity(qwen_ans, gold_ans)
    base_score = similarity(base_ans, gold_ans)

    # Store everything in one place
    results[q] = {
        "gold": gold_ans,
        "qwen_answer": qwen_ans,
        "base_answer": base_ans,
        "qwen_score": round(qwen_score, 3),
        "base_score": round(base_score, 3)
    }

# ---- Save combined outputs ----
json.dump(results, open("evaluated.json", "w"), indent=2)

# ---- Print averages ----
avg_qwen = sum(r["qwen_score"] for r in results.values()) / len(results)
avg_base = sum(r["base_score"] for r in results.values()) / len(results)

print("Average QWEN Score:", round(avg_qwen, 3))
print("Average Base Score:", round(avg_base, 3))
print("Saved full evaluation → evaluated.json")
