import {
  type FileExists,
  RegistryName,
  CommonPaths,
  type Readme,
} from "$lib/scripts/types";
import { getReadme } from "$lib/scripts/utils";
import { apiHandler } from "$lib/scripts/apiHandler";

const opsmlRoot: string = `opsml-root:/${RegistryName.Model}`;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const name: string = (url as URL).searchParams.get("name");
  const repository: string = (url as URL).searchParams.get("repository");
  const version: string = (url as URL).searchParams.get("version");
  let status: string = (url as URL).searchParams.get("status");

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
