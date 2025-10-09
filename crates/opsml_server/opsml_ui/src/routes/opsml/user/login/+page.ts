export const ssr = false;

import { UiPaths } from "$lib/utils/api/routes";
import type { PageLoad } from "./$types";

export const load: PageLoad = ({ url }) => {
  const currentPath = (url as URL).pathname;
  let previousPath = (url as URL).searchParams.get("redirect") as
    | string
    | undefined;

  if (previousPath === UiPaths.LOGIN || previousPath === UiPaths.REGISTER) {
    previousPath = UiPaths.HOME;
  }

  return {
    currentPath,
    previousPath,
  };
};
