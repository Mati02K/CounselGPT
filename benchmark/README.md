## Benchmarking Setup (k6 Load Testing)

This folder contains all performance testing scripts used for **load**, **stress**, **spike**, and **soak** testing with **k6**.

## 1. Install k6 (if not in the system)

### **Linux (Debian/Ubuntu)**

```bash
sudo apt update
sudo apt install -y gnupg software-properties-common
curl -s https://dl.k6.io/key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/k6-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt update
sudo apt install -y k6
```

### **Mac (Homebrew)**

```bash
brew install k6
```

### **Windows**

Download from:
[https://github.com/grafana/k6/releases](https://github.com/grafana/k6/releases)

---

## 2. Environment Switching (Local → Nautilus → GCP)

Reach out to mthriuma@ucsc.edu for env files.

---

## 3. Load `.env` Variables (Only Once Per Terminal Session)

Every time you open a **new terminal**, run:

```bash
source .env
```

After this, all three variables (`API_URL_LOCAL`, `API_URL_GCP`, `API_URL_NAUTILUS`) are available for k6.

---

## 4. Running Benchmark Scripts

Each script accepts a runtime variable `API_URL`.

### **Local Testing**

```bash
k6 run benchmark/loadtest.js -e API_URL=$API_URL_LOCAL
```

### **GCP Production Testing**

```bash
k6 run benchmark/stresstest.js -e API_URL=$API_URL_GCP
```

### **Nautilus Deployment Testing**

```bash
k6 run benchmark/spiketest.js -e API_URL=$API_URL_NAUTILUS
```

---
