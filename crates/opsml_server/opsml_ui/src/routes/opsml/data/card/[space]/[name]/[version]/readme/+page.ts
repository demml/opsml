import type { PageLoad } from "./$types";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

export const load: PageLoad = async ({ parent }) => {
  await validateUserOrRedirect();
  const { metadata, registryType, readme } = await parent();

  let content: string = "";

  if (readme.exists) {
    content = readme.readme;
  } else {
    content = `# DataCard for ${metadata.space}/${metadata.name}

<!--- Brief summary of the data card, its purpose, and key highlights. -->

**Summary:**  
Provide a concise summary of the data card, its intended use, and any notable features.

---

## Model Details

- **Space:** ${metadata.space}
- **Name:** ${metadata.name}
- **Version:** ${metadata.version}
- **Registry:** ${registryType}

---

## Description

Describe the model or dataset in detail.  
Include its origin, intended use cases, and any relevant background information.

---

## Contact

- **Contact Person/Team:** [Add contact information or support email]
- **License:** [Specify license, e.g., MIT, Apache 2.0, etc.]

---

## Data Development

Explain how the data/model was developed, including sources, methodology, and any preprocessing steps.

---

## Uses

List and describe common or recommended uses for this data card.

---

## Bias, Risk, and Limitations

<!--- Credit: HuggingFace Model Card template -->

Discuss any known biases, risks, or limitations associated with this data/model.  
Mention steps taken to mitigate these issues, if any.

---

## Code Examples

<!--- Provide code snippets or usage examples for this data card. -->
\`\`\`python
# Example usage in Python
from opsml import CardRegistry
registry = CardRegistry("${registryType.toLowerCase()}")
card = registry.load_card(uid="${metadata.uid}")
\`\`\`

`;
  }

  return {
    metadata,
    content,
  };
};
