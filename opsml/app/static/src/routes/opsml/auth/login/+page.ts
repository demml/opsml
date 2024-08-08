export const ssr = false;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  let currentPath = url.pathname;
  let previousPath: string | null = url.searchParams.get("url");

  return {
    currentPath,
    previousPath,
  };
}
