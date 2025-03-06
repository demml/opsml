import { RoutePaths } from "$lib/components/api/routes";
import type { PageLoad } from "./$types";

export const ssr = false;

export const load: PageLoad = ({ url }) => {
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
};
