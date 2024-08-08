export const ssr = false;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  let previousPath: string | null = url.searchParams.get("url");

  if (previousPath === null) {
    previousPath = "/opsml/auth/login";
  }

  return {
    previousPath,
  };
}