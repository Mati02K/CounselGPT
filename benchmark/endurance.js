import http from 'k6/http';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

export const options = {
  vus: 50,              // steady 20 concurrent users (adjustable)
  duration: '2h',       // endurance duration
  thresholds: {
    http_req_duration: ['p(95) < 40000'],   // fail if > 40 seconds
    http_req_failed: ['rate < 0.01'],      // fail if > 1% failures
  },
};

const API_URL = __ENV.API_URL;

// Large legal-domain prompt list
const prompts = JSON.parse(open('./prompts/testclear.json'));

export default function () {
  const prompt = randomItem(prompts);

  const payload = JSON.stringify({
    prompt: prompt,
    max_tokens: 80,
    use_cache: false,
  });

  http.post(API_URL, payload, {
    headers: { 'Content-Type': 'application/json' },
  });
}
