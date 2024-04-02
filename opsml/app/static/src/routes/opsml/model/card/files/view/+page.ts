/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  let filePath = atob(url.searchParams.get("path"));

  console.log(filePath);

  let viewData = await fetch(`/opsml/files/presign?path=${filePath}`).then(
    (res) => res.json()
  );

  return viewData;
}
