import http from 'k6/http';

export const options = {
  stages: [
    { duration: '30s', target: 5 },   // ramp to 5 RPS
    { duration: '30s', target: 10 },  // to 10 RPS
    { duration: '30s', target: 20 },  // to 20 RPS
    { duration: '30s', target: 30 },  // push to 30 RPS
    { duration: '30s', target: 0 },   // cooldown
  ],
};

const API_URL = "https://counselgpt-mathesh.nrp-nautilus.io/infer";

// Five prompts to avoid Redis cache 
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
    max_tokens: 50
  });

  http.post(API_URL, payload, {
    headers: { 'Content-Type': 'application/json' },
  });
}
