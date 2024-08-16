import { CommonPaths } from "$lib/scripts/types";
export const ssr = false;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  let currentPath = url.pathname;
  let previousPath: string | null = url.searchParams.get("redirect");

  if (
    previousPath === CommonPaths.LOGIN ||
    previousPath === CommonPaths.REGISTER
  ) {
    previousPath = CommonPaths.HOME;
  }

  return {
    currentPath,
    previousPath,
  };
}
