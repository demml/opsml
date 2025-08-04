import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent, url }) => {
  const name = (url as URL).searchParams.get("name") as string;
  const space = (url as URL).searchParams.get("space") as string;

  const { metadata, registry, readme } = await parent();

  let content: string = "";

  if (readme.exists) {
    content = readme.readme;
  } else {
    content = `# PromptCard Description for ${name} 

<!--- Summary of prompt goes here -->

Generic summary for ${space}/${name} goes here.

## Prompt Details

## Description

This section is used to describe the prompt in more detail.

- ** Contact: ** [Provide contact information here]
- ** License: ** [Provide license information here]

## Prompt Development

This section is used to describe the prompt development process.

## Uses

This section is used to describe the uses of the prompt.

## Bias, Risk, and Limitations

<!--- This section is used to describe the bias, risk, and limitations of the prompt. Credit to huggingface template -->

Provide a brief description of the bias, risk, and limitations of the prompt.

## Code Examples

<!--- This section is used to provide code examples for the prompt -->
    `;
  }

  return {
    metadata,
    registry,
    content,
  };
};
