# **CounselGPT Benchmark Suite (k6 Performance Testing)**

This folder contains the complete performance benchmarking framework for evaluating **Qwen** and **Llama** inference on **Nautilus** and **GCP** deployments using **k6**.

The test suite supports:

* Load tests
* Stress tests
* Spike tests
* Soak (long-duration) tests
* Endurance tests
* GPU vs CPU
* Cache vs No-cache
* Small vs large reasoning prompts

All configuration is cleanly separated into `params.json`, and each scenario uses a shared `common.js` executor.

---

# **Directory Structure**

```
benchmark/
│
├── config/
│   ├── params.json          # All model configs, URLs, prompt paths
│   └── prompts/
│       ├── small.json       # Small simple prompts
│       ├── similar.json     # Similar prompts (for cache testing)
│       └── large.json       # Long reasoning prompts
│
├── scenarios/
│   ├── load.js              # Load test (ramp-up sustained load)
│   ├── stress.js            # Stress test (push until failure)
│   ├── spike.js             # Sudden spike test
│   ├── soak.js              # Long-duration reliability test
│   └── endurance.js         # Resource stability test over time
│
├── results/                 # k6 result outputs are stored here
│
├── modelBenchmark/          # Offline model-only benchmarks (not cloud tests)
│   └── (ignored by cloud testing)
│
├── common.js                # Shared execution logic for all scenarios
└── README.md                # Documentation
```

✔ **`modelBenchmark/` is kept for model testing, but NOT used for cloud testing.**
✔ Cloud tests only use **config/**, **scenarios/**, **common.js**, and **results/**.

---

# 1. **Installing k6**

### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install -y gnupg software-properties-common
curl -s https://dl.k6.io/key.gpg \
  | sudo gpg --dearmor -o /usr/share/keyrings/k6-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" \
  | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt update
sudo apt install -y k6
```

### MacOS

```bash
brew install k6
```

### Windows

Download from:
[https://github.com/grafana/k6/releases](https://github.com/grafana/k6/releases)

---

# 2. **Configuration Using params.json**

All test parameters (model, GPU, cache, max_tokens, prompt set, API URL) live inside:

```
config/params.json
```

You select which configuration to run via:

```
-e CONFIG=<name>
```

Example config key:

```
qwen_gpu_on_nautilus
```

---

# 3. **How to Run a Scenario**

All scenarios import `common.js`, which handles:

* loading the selected params.json entry
* loading prompts
* posting to configured API URL

Run any scenario like:

```bash
k6 run scenarios/load.js -e CONFIG=qwen_gpu_on_nautilus > results/qwen_gpu_on_nautilus_load.txt
```

---

# 4. **List of All Tests Required (1–9)**

Below is **exactly the test matrix to cover all edge cases**

Naming convention:

```
results/<config>_<scenario>.txt
```

---

# **TEST GROUP 1: Qwen, GPU ON, No Cache, Normal Prompts**

Run on: load, stress, soak, spike, endurance

```
k6 run scenarios/load.js -e CONFIG=qwen_gpu_on_nautilus > results/qwen_nautilus_load.txt
k6 run scenarios/spike.js -e CONFIG=qwen_gpu_on_nautilus > results/qwen_nautilus_spike.txt
k6 run scenarios/soak.js -e CONFIG=qwen_gpu_on_nautilus > results/qwen_nautilus_soak.txt
k6 run scenarios/stress.js -e CONFIG=qwen_gpu_on_nautilus > results/qwen_nautilus_stress.txt
k6 run scenarios/endurance.js -e CONFIG=qwen_gpu_on_nautilus > results/qwen_nautilus_endurance.txt
```

---

# **TEST GROUP 2: Llama (4-bit), GPU ON, No Cache, Normal Prompts**

```
k6 run scenarios/load.js      -e CONFIG=llama_gpu_on_nautilus > results/llama_gpu_on_nautilus_load.txt
k6 run scenarios/stress.js    -e CONFIG=llama_gpu_on_nautilus > results/llama_gpu_on_nautilus_stress.txt
k6 run scenarios/soak.js      -e CONFIG=llama_gpu_on_nautilus > results/llama_gpu_on_nautilus_soak.txt
k6 run scenarios/spike.js     -e CONFIG=llama_gpu_on_nautilus > results/llama_gpu_on_nautilus_spike.txt
k6 run scenarios/endurance.js -e CONFIG=llama_gpu_on_nautilus > results/llama_gpu_on_nautilus_endurance.txt
```

---

# **TEST GROUP 3: Qwen GPU OFF, No Cache, Normal Prompts (Load Test Only)**

```
k6 run scenarios/load.js -e CONFIG=qwen_gpu_off_nautilus > results/qwen_gpu_off_nautilus_load.txt
```

---

# **TEST GROUP 4: Llama GPU OFF, No Cache, Normal Prompts (Load Only)**

```
k6 run scenarios/load.js -e CONFIG=llama_gpu_off_nautilus > results/llama_gpu_off_nautilus_load.txt
```

---

# **TEST GROUP 5: Qwen GPU ON, Cache ON, Similar Prompts**

(load, stress, soak, spike, endurance)

```
k6 run scenarios/load.js      -e CONFIG=qwen_cache_nautilus_similar > results/qwen_cache_nautilus_similar_load.txt
k6 run scenarios/stress.js    -e CONFIG=qwen_cache_nautilus_similar > results/qwen_cache_nautilus_similar_stress.txt
k6 run scenarios/soak.js      -e CONFIG=qwen_cache_nautilus_similar > results/qwen_cache_nautilus_similar_soak.txt
k6 run scenarios/spike.js     -e CONFIG=qwen_cache_nautilus_similar > results/qwen_cache_nautilus_similar_spike.txt
k6 run scenarios/endurance.js -e CONFIG=qwen_cache_nautilus_similar > results/qwen_cache_nautilus_similar_endurance.txt
```

---

# **TEST GROUP 6: Qwen GPU ON, No Cache, Large Reasoning Prompts (Load Only)**

```
k6 run scenarios/load.js -e CONFIG=qwen_large > results/qwen_large_load.txt
```

---

# **TEST GROUP 7: Llama GPU ON, No Cache, Large Reasoning Prompts (Load Only)**

```
k6 run scenarios/load.js -e CONFIG=llama_large > results/llama_large_load.txt
```

---

# **TEST GROUP 8: GCP vs Nautilus**

Nautilus -> take the results from step 1.

GCP
```
k6 run scenarios/load.js -e CONFIG=qwen_gpu_on_gcp > results/qwen_gcp_load.txt
k6 run scenarios/spike.js -e CONFIG=qwen_gpu_on_gcp > results/qwen_gcp_spike.txt
k6 run scenarios/soak.js -e CONFIG=qwen_gpu_on_gcp > results/qwen_gcp_soak.txt
k6 run scenarios/stress.js -e CONFIG=qwen_gpu_on_gcp > results/qwen_gcp_stress.txt
```

---


# **TEST GROUP 9: Small Prompts**

Nautilus
```
k6 run scenarios/load.js -e CONFIG=qwen_gpu_on_nautilus_small > results/qwen_nautilus_small_load.txt
k6 run scenarios/spike.js -e CONFIG=qwen_gpu_on_nautilus_small > results/qwen_nautilus_small_spike.txt
k6 run scenarios/stress.js -e CONFIG=qwen_gpu_on_nautilus_small > results/qwen_nautilus_small_stress.txt
```

GCP
```
k6 run scenarios/load.js -e CONFIG=qwen_gpu_on_gcp_small > results/qwen_gcp_small_load.txt
k6 run scenarios/spike.js -e CONFIG=qwen_gpu_on_gcp_small > results/qwen_gcp_small_spike.txt
k6 run scenarios/stress.js -e CONFIG=qwen_gpu_on_gcp_small > results/qwen_gcp_small_stress.txt
```

---