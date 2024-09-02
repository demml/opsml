import { RegistryName, type Readme } from "$lib/scripts/types";
import { getReadme } from "$lib/scripts/utils";

const opsmlRoot: string = `opsml-root:/${RegistryName.Model}`;

/** @type {import('./$types').PageLoad} */
export async function load({ url }) {
  const name = (url as URL).searchParams.get("name") as string | undefined;
  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;
  const version = (url as URL).searchParams.get("version") as
    | string
    | undefined;
  let status = (url as URL).searchParams.get("status") as string | undefined;

  status = "edit";

  let content: string = "";

  // check if markdown exists
  const markdownPath = `${opsmlRoot}/${repository}/${name}/README.md`;
  const readme: Readme = await getReadme(markdownPath);

  if (readme.exists) {
    content = readme.readme;
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
    version,
    content,
  };
}
