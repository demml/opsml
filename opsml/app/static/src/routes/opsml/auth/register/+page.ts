export const ssr = false;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  let previousPage: string | null = url.searchParams.get("url");

  if (previousPage === null) {
    previousPage = "/opsml/auth/login";
  }

  return {
    previousPage,
  };
}
