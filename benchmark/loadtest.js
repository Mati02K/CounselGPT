import http from 'k6/http';
import { sleep } from 'k6';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

export const options = {
  vus: 5,
  duration: '2m',
  thresholds: {
    http_req_duration: ['p(95) < 5000'],   // fail if > 8s
    http_req_failed: ['rate < 0.05'],      // fail if > 5% failures
  }
};

// const prompts = JSON.parse(open('./prompts/longprompts.json'));
// const prompts = JSON.parse(open('./prompts/smallprompts.json'));
const prompts = JSON.parse(open('./prompts/testclear.json'));

const API_URL = __ENV.API_URL;

export default function () {
  const prompt = randomItem(prompts);

  const payload = JSON.stringify({
    prompt: prompt,
    max_tokens: 150,
    use_cache: true,
  });

  const res = http.post(API_URL, payload, {
    headers: { 'Content-Type': 'application/json' },
  });

  sleep(0.3);
}


// This is how it will work (for me to intepret)
// VU1: send — wait 0.3 — send — wait
// VU2: send — wait 0.3 — send — wait
// VU3: send — wait 0.3 — send — wait