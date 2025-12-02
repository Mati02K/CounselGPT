import http from 'k6/http';
import { sleep } from 'k6';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

export const options = {
  vus: 10,                // 10 concurrent users
  duration: '2m',         // run for 2 minutes
  timeout: '120s',        // allow long inference
};

// const API_URL = "https://counselgpt-mathesh.nrp-nautilus.io/infer";
// const API_URL = "http://localhost:8000/infer";
// const API_URL = "https://136.110.236.198.nip.io/infer";
const API_URL = __ENV.API_URL;


// Five prompts to avoid Redis cache 
// TODO make more prompts (like 100)
const prompts = [
  "Explain fraud in simple terms.",
  "What is vessel in Law?.",
  "I am a immigrant what are the rules I should know before travelling outside US?",
  "What are the things I need to verify in my legal agreement.",
  "Give a short overview of taffic laws in Nashville."
];


export default function () {
  const prompt = randomItem(prompts);

  const payload = JSON.stringify({
    prompt: prompt,
    max_tokens: 150,
    use_cache: false,
  });

  const res = http.post(API_URL, payload, {
    headers: { 'Content-Type': 'application/json' },
  });

  sleep(0.5);   // small pause
}


//  run using k6 run loadtest.js