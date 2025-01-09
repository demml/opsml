export const ssr = false;

/** @type {import('./$types').PageLoad} */
export function load({ url }) {
  const message = (url as URL).searchParams.get("message") as
    | string
    | undefined;
  return {
    message: message!,
  };
}
