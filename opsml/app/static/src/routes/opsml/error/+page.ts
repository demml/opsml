export const ssr = false;

/** @type {import('./$types').PageLoad} */
export function load({ fetch, params, url }) {
  const error = (url as URL).searchParams.get("error") as string | undefined;
  return {
    error: error!,
  };
}
