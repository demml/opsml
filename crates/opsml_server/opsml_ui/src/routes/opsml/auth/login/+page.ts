import { CommonPaths } from "$lib/scripts/types";

export const ssr = false;

/** @type {import('./$types').PageLoad} */
export function load({ url }) {
  const currentPath = (url as URL).pathname;
  let previousPath = (url as URL).searchParams.get("redirect") as
    | string
    | undefined;

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
