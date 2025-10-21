import { UiPaths } from "$lib/components/api/routes";
import type { PageLoad } from "./$types";

export const load: PageLoad = ({ url }) => {
  let previousPath = (url as URL).searchParams.get("redirect") as
    | string
    | undefined;

  if (previousPath === UiPaths.LOGIN || previousPath === UiPaths.REGISTER) {
    previousPath = UiPaths.HOME;
  }

  return {
    previousPath,
  };
};
