import type { PageLoad } from "./$types";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

export const load: PageLoad = async ({ parent }) => {
  await validateUserOrRedirect();
  const { metadata, registryType, readme, registryPath } = await parent();

  let content: string = "";

  if (readme.exists) {
    content = readme.readme;
  } else {
    content = `# ModelCard for ${metadata.space}/${metadata.name}

<!--- Brief summary of the model card, its purpose, and key highlights. -->

**Summary:**  
Provide a concise summary of the model card, its intended use, and any notable features.

---

## Model Details

- **Space:** ${metadata.space}
- **Name:** ${metadata.name}
- **Version:** ${metadata.version}
- **Registry:** ${registryType}

---

## Description

Describe the model in detail.  
Include its origin, intended use cases, and any relevant background information.

---

## Contact

- **Contact Person/Team:** [Add contact information or support email]
- **License:** [Specify license, e.g., MIT, Apache 2.0, etc.]

---

## Model Development

Explain how the model was developed, including sources, methodology, and any preprocessing steps.

---

## Uses

List and describe common or recommended uses for this model card.

---

## Bias, Risk, and Limitations

Discuss any known biases, risks, or limitations associated with this model.  
Mention steps taken to mitigate these issues, if any.

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
