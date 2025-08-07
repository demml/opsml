import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent, url }) => {
  const name = (url as URL).searchParams.get("name") as string;
  const space = (url as URL).searchParams.get("space") as string;

  const { metadata, registry, readme } = await parent();

  let content: string = "";

  if (readme.exists) {
    content = readme.readme;
  } else {
    content = `# ModelCard Description for ${name} 

<!--- Summary of model goes here -->

Generic summary for ${space}/${name} goes here.

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
    metadata,
    registry,
    content,
  };
};
