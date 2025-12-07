import { runTest } from "../common.js";

export const options = {
  vus: 15,
  duration: "10m",   // small endurance test as such
};

export default function () {
  runTest();
}
