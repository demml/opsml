export const ssr = false;

import { RoutePaths, UiPaths } from "$lib/components/api/routes";
import type { PageLoad } from "./$types";

export const load: PageLoad = ({ url }) => {
  const currentPath = (url as URL).pathname;
  let previousPath = (url as URL).searchParams.get("redirect") as
    | string
    | undefined;

  if (previousPath === UiPaths.LOGIN || previousPath === UiPaths.REGISTER) {
    previousPath = UiPaths.HOME;
  }

  console.log("Login");

  return {
    currentPath,
    previousPath,
  };
};
