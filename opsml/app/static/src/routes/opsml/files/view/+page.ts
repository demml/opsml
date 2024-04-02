/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  let filePath = url.searchParams.get("path");

  let viewData = await fetch(`/opsml/files/presign?path=${filePath}`).then(
    (res) => res.json()
  );

  console.log(viewData);
}
