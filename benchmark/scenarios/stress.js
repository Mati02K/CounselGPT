import { runTest } from "../common.js";

export const options = {
  stages: [
    { duration: '20s', target: 5 },    // low load
    { duration: '20s', target: 10 },   // moderate load
    { duration: '20s', target: 15 },   // high load
    { duration: '20s', target: 20 },   // pushing limits
    { duration: '20s', target: 25 },   // beyond typical safe limits
    { duration: '10s', target: 0 },    // cooldown
  ]
};

export default function () {
  runTest();
}
