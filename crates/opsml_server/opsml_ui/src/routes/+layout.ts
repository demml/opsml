export const prerender = true;
export const ssr = false;

// @ts-ignore
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async () => {
  return {};
};
