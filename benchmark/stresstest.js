import http from 'k6/http';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

export const options = {
  stages: [
    { duration: '20s', target: 5 },    // low load
    { duration: '20s', target: 10 },   // moderate load
    { duration: '20s', target: 20 },   // high load
    { duration: '20s', target: 30 },   // pushing limits
    { duration: '20s', target: 40 },   // beyond typical safe limits
    { duration: '10s', target: 0 },    // cooldown
  ],
  thresholds: {
    http_req_duration: ['p(95) < 8000'],   // fail if > 8s
    http_req_failed: ['rate < 0.05'],      // fail if > 5% failures
  },
};

const API_URL = __ENV.API_URL;

// Full legal-domain test prompts
const prompts = JSON.parse(open('./prompts/testclear.json'));

export default function () {
  const prompt = randomItem(prompts);

  const payload = JSON.stringify({
    prompt,
    max_tokens: 50,
    use_cache: false,
  });

  http.post(API_URL, payload, {
    headers: { 'Content-Type': 'application/json' },
  });
}
