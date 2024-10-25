export const prerender = true;

/** @type {import('./$types').LayoutLoad} */
export async function load({}) {
  console.log("layout load");
  return {};
}
