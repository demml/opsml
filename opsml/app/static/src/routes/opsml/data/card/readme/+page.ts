import { RegistryName, type Readme } from "$lib/scripts/types";
import { getReadme } from "$lib/scripts/utils";

const opsmlRoot: string = `opsml-root:/${RegistryName.Data}`;

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
