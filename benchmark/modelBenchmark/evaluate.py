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
    r_llama = requests.post(API_URL, json={
        "prompt": q,
        "max_tokens": 200,
        "model_name": "llama",
        "use_cache": False
    }).json()

    llama_ans = r_llama["response"]

    # ---- Score against gold ----
    gold_ans = gold[q]

    qwen_score = similarity(qwen_ans, gold_ans)
    llama_score = similarity(llama_ans, gold_ans)

    # Store everything in one place
    results[q] = {
        "gold": gold_ans,
        "qwen_answer": qwen_ans,
        "llama_answer": llama_ans,
        "qwen_score": round(qwen_score, 3),
        "llama_score": round(llama_score, 3)
    }

# ---- Save combined outputs ----
json.dump(results, open("evaluated.json", "w"), indent=2)

# ---- Print averages ----
avg_qwen = sum(r["qwen_score"] for r in results.values()) / len(results)
avg_llama = sum(r["llama_score"] for r in results.values()) / len(results)

print("Average QWEN Score:", round(avg_qwen, 3))
print("Average LLaMA Score:", round(avg_llama, 3))
print("Saved full evaluation → evaluated.json")
