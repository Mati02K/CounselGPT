import http from 'k6/http';

export const options = {
  vus: 0,
  stages: [
    { duration: '1s', target: 0 },   // idle
    { duration: '1s', target: 25 },  // sudden spike to 25 users
    { duration: '20s', target: 25 }, // hold spike
    { duration: '1s', target: 0 },   // drop
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
    max_tokens: 60
  });

  http.post(API_URL, payload, {
    headers: { 'Content-Type': 'application/json' },
  });
}
