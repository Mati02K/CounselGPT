import http from 'k6/http';
import { sleep } from 'k6';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

export const options = {
  vus: 5,             // small constant load
  duration: '10m',    // long enough to detect degradation
  thresholds: {
    http_req_duration: ['p(95) < 8000'],   // fail if > 8s
    http_req_failed: ['rate < 0.05'],      // fail if > 5% failures
  },
};

// Load large legal-domain prompt list
const prompts = JSON.parse(open('./prompts/testclear.json'));

const API_URL = __ENV.API_URL;

export default function () {
  const prompt = randomItem(prompts);

  const payload = JSON.stringify({
    prompt: prompt,
    max_tokens: 80,
    use_cache: false,     // avoid Redis hide problems
  });

  http.post(API_URL, payload, {
    headers: { 'Content-Type': 'application/json' },
  });

  sleep(0.5);  // moderate request spacing
}
