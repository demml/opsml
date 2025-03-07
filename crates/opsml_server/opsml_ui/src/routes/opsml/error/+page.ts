export const ssr = false;
import type { PageLoad } from "./$types";

export const load: PageLoad = ({ url }) => {
  const message = (url as URL).searchParams.get("message") as
    | string
    | undefined;

  return {
    message: message!,
  };
};
