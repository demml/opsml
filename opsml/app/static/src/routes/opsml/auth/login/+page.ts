import { CommonPaths } from "$lib/scripts/types";

export const ssr = false;

/** @type {import('./$types').PageLoad} */
export function load({ fetch, params, url }) {
  const currentPath = (url as URL).pathname;
  let previousPath: string | null = (url as URL).searchParams.get("redirect");

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
