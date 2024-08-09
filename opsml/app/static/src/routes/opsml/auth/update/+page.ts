export const ssr = false;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  let type: string = url.searchParams.get("type");

  return {
    type,
  };
}
