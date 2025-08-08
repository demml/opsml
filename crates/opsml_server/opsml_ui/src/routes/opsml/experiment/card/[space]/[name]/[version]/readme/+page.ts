import type { PageLoad } from "./$types";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

export const load: PageLoad = async ({ parent }) => {
  await validateUserOrRedirect();
  const { metadata, registryType, readme, registryPath } = await parent();

  let content: string = "";

  if (readme.exists) {
    content = readme.readme;
  } else {
    content = `# ExperimentCard for ${metadata.space}/${metadata.name}

<!--- Brief summary of the experiment card, its purpose, and key highlights. -->

**Summary:**  
Provide a concise summary of the experiment card, its intended use, and any notable features.

---

## Experiment Details

- **Space:** ${metadata.space}
- **Name:** ${metadata.name}
- **Version:** ${metadata.version}
- **Registry:** ${registryType}

---

## Description

Describe the experiment in detail.  
Include its origin, intended use cases, and any relevant background information.

---

## Experiment Development

Explain how the experiment was developed, including sources, methodology, and any preprocessing steps.

---

## Code Examples

<!--- Provide code snippets or usage examples for this model card. -->
\`\`\`python
# Example usage in Python
from opsml import CardRegistry
registry = CardRegistry("${registryPath}")
card = registry.load_card(uid="${metadata.uid}")
\`\`\`

`;
  }

  return {
    metadata,
    content,
  };
};
