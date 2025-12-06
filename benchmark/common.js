import http from "k6/http";
import { sleep } from "k6";
import { randomItem } from "https://jslib.k6.io/k6-utils/1.4.0/index.js";

// Load config by key
const config = JSON.parse(open("./config/params.json"))[
  __ENV.CONFIG
];

if (!config) {
  throw new Error(`CONFIG "${__ENV.CONFIG}" not found in params.json`);
}

// Load prompts from file inside the config
const prompts = JSON.parse(open(config.prompts));

// API URL comes from config now
const API_URL = config.api_url;

export function runTest() {
  const prompt = randomItem(prompts);

  const payload = JSON.stringify({
    prompt: prompt,
    max_tokens: config.max_tokens,
    model_name: config.model,
    use_gpu: config.use_gpu,
    use_cache: config.use_cache
  });

  http.post(API_URL, payload, {
    headers: { "Content-Type": "application/json" }
  });

  sleep(0.2);
}
