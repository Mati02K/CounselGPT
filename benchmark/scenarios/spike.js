import { runTest } from "../common.js";

export const options = {
  stages: [
    { duration: '2s', target: 0 },    // idle
    { duration: '2s', target: 25 },   // INSTANT SPIKE to 25 VUs
    { duration: '15s', target: 25 },  // HOLD high load
    { duration: '2s', target: 0 },    // DROP to zero
  ]
};

export default function () {
  runTest();
}
