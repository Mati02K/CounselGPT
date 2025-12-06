import { runTest } from "../common.js";

export const options = {
  stages: [
    { duration: "30s", target: 10 },
    { duration: "30s", target: 25 },
    { duration: "30s", target: 50 },
    { duration: "30s", target: 0 }
  ]
};

export default function () {
  runTest();
}
