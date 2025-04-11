import { getCardReadMe, type ReadMe } from "$lib/components/readme/util";
import { RegistryType } from "$lib/utils";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent, url }) => {
  const name = (url as URL).searchParams.get("name") as string;
  const space = (url as URL).searchParams.get("space") as string;

  const { metadata, registry, readme } = await parent();

  let content: string = "";

  if (readme.exists) {
    content = readme.readme;
  } else {
    content = `# ExperimentCard Description for ${name} 

<!--- Summary of experiment goes here -->

Generic summary for ${space}/${name} goes here.

## Experiment Details

## Description

This section is used to describe the experiment in more detail.

- ** Contact: ** [Provide contact information here]
- ** License: ** [Provide license information here]
    `;
  }

  return {
    metadata,
    registry,
    content,
  };
};
