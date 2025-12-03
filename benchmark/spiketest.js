import http from 'k6/http';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

export const options = {
  stages: [
    { duration: '2s', target: 0 },    // idle
    { duration: '2s', target: 100 },   // INSTANT SPIKE to 30 VUs
    { duration: '15s', target: 100 },  // HOLD high load
    { duration: '2s', target: 0 },    // DROP to zero
  ],
  thresholds: {
    http_req_duration: ['p(95) < 8000'],   // fail if > 8s
    http_req_failed: ['rate < 0.05'],      // fail if > 5% failures
  },
};

const API_URL = __ENV.API_URL;

// Load from your cleaned prompt list
const prompts = JSON.parse(open('./prompts/testclear.json'));

export default function () {
  const prompt = randomItem(prompts);

  const payload = JSON.stringify({
    prompt: prompt,
    max_tokens: 60,
    use_cache: false,
  });

  http.post(API_URL, payload, {
    headers: { 'Content-Type': 'application/json' },
  });
}

// First 2 sec: Nothing

// Next 2 sec: k6 ramps from 0 to 30 VUs (SPIKE)

// Next 15 sec: 30 VUs hammer the API continuously

// Last 2 sec: Load drops to zero