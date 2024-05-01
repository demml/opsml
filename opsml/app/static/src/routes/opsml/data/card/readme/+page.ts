import { type FileExists, RegistryName } from "$lib/scripts/types";

const opsmlRoot: string = `opsml-root:/${RegistryName.Data}`;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const name: string = url.searchParams.get("name")!;
  const repository: string = url.searchParams.get("repository")!;
  const version: string = url.searchParams.get("version")!;
  let status: string = url.searchParams.get("status")!;

  status = "edit";

  // check if markdown exists
  const markdownPath = `${opsmlRoot}/${repository}/${name}/README.md`;

  const markdown: FileExists = await fetch(
    `/opsml/files/exists?path=${markdownPath}`
  ).then((res) => res.json());

  let content: string = "";
  if (markdown.exists) {
    // fetch markdown
    const viewData = await fetch(`/opsml/files/view?path=${markdownPath}`).then(
      (res) => res.json()
    );

    content = viewData.content.content;
  } else {
    content = `# DataCard Description for ${name} 

<!--- Summary of data goes here -->

Generic summary for ${repository}/${name} goes here.

## Data Details

## Description

This section is used to describe the data in more detail.

- ** Contact: ** [Provide contact information here]
- ** License: ** [Provide license information here]

## Data Development

This section is used to describe the data development process.

## Uses

This section is used to describe the uses of the data.

## Bias, Risk, and Limitations

<!--- This section is used to describe the bias, risk, and limitations of the data. Credit to huggingface template -->

Provide a brief description of the bias, risk, and limitations of the data.


    `;
  }

  return {
    status,
    name,
    repository,
    registry: "data",
    version,
    content,
  };
}
