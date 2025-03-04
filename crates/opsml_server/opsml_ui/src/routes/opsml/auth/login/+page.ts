import { RoutePaths } from "$lib/components/api/routes";

export const ssr = false;

/** @type {import('./$types').PageLoad} */
export function load({ url }) {
  const currentPath = (url as URL).pathname;
  let previousPath = (url as URL).searchParams.get("redirect") as
    | string
    | undefined;

  if (
    previousPath === RoutePaths.LOGIN ||
    previousPath === RoutePaths.REGISTER
  ) {
    previousPath = RoutePaths.HOME;
  }

  return {
    currentPath,
    previousPath,
  };
}
