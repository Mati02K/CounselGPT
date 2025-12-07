import { runTest } from "../common.js";

export const options = {
  vus: 5,
  duration: "2m",
  // Commenting the thresholds because we are yet to finalize what should be considered fine
  // thresholds: {
  //   http_req_duration: ["p(95) < 5000"],
  //   http_req_failed: ["rate < 0.05"]
  // }
};

export default function () {
  runTest();
}
