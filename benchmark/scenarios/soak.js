import { runTest } from "../common.js";

export const options = {
  vus: 5,
  duration: "30m",   // or 1hr depending on what you want
};

export default function () {
  runTest();
}
