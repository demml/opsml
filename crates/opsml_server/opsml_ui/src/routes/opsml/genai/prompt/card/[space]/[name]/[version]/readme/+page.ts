import type { PageLoad } from "./$types";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

export const load: PageLoad = async ({ parent }) => {
  const { metadata, registryType, readme, registryPath } = await parent();

  let content: string = "";

  if (readme.exists) {
    content = readme.readme;
  } else {
    content = `# Prompt Card for ${metadata.space}/${metadata.name}

**Summary:**  
Briefly describe what this prompt does and its main purpose.

---

## Details

- **Space:** ${metadata.space}
- **Name:** ${metadata.name}
- **Version:** ${metadata.version}
- **Registry:** ${registryType}

---

## Description

Describe the prompt in detail, including its intended use, context, and any relevant background.

---

## Development Notes

Explain how the prompt was created, including any sources, methodology, or special considerations.

---

## Example Usage

\`\`\`python
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
