import { type FileExists, RegistryName } from "$lib/scripts/types";

const opsmlRoot: string = `opsml-root:/${RegistryName.Model}`;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const name: string = url.searchParams.get("name")!;
  const repository: string = url.searchParams.get("repository")!;
  let status: string = url.searchParams.get("status")!;

  status = "edit";

  // check if markdown exists
  const markdownPath = `${opsmlRoot}/${repository}/${name}/README.md`;

  const markdown: FileExists = await fetch(
    `/opsml/files/exists?path=${markdownPath}`,
  ).then((res) => res.json());

  let content: string = "";
  if (markdown.exists) {
    // fetch markdown
    const viewData = await fetch(`/opsml/files/view?path=${markdownPath}`).then(
      (res) => res.json(),
    );

    content = viewData.content.content;
  } else {
    content = `# ModelCard Description for ${name} 

<!--- Summary of model goes here -->

Generic summary for ${repository}/${name} goes here.

## Model Details

## Description

This section is used to describe the model in more detail.

- ** Contact: ** [Provide contact information here]
- ** License: ** [Provide license information here]

## Model Development

This section is used to describe the model development process.

## Uses

This section is used to describe the uses of the model.

## Bias, Risk, and Limitations

<!--- This section is used to describe the bias, risk, and limitations of the model. Credit to huggingface template -->

Provide a brief description of the bias, risk, and limitations of the model.

## Code Examples

<!--- This section is used to provide code examples for the model -->

    `;
  }

  return {
    status,
    name,
    repository,
    registry: "model",
    content,
  };
}
