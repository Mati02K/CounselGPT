import { runTest } from "../common.js";

export const options = {
  stages: [
    { duration: "5s", target: 1 },
    { duration: "3s", target: 40 },
    { duration: "20s", target: 1 }
  ]
};

export default function () {
  runTest();
}
