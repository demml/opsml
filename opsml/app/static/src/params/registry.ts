import type { ParamMatcher } from "@sveltejs/kit";

// create function to check if registry param is model or data
export function match(param) {
  return param === "models" || param === "data";
}
