import { RegistryType } from "$lib/utils";
/**
 * Common metadata interface for all card types
 */
export interface CardMetadata {
  space: string;
  name: string;
  version: string;
  uid: string;
}

/**
 * Readme data interface
 */
export interface ReadmeData {
  exists: boolean;
  readme?: string;
}

/**
 * Registry-specific readme template generators
 */
// @ts-ignore
export const readmeTemplates: Record<
  RegistryType,
  (metadata: CardMetadata, registryType: string) => string
> = {
  [RegistryType.Data]: (
    metadata: CardMetadata,
    registryType: string
  ): string => `# DataCard for ${metadata.space}/${metadata.name}

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
`,

  [RegistryType.Model]: (
    metadata: CardMetadata,
    registryType: string
  ): string => `# ModelCard for ${metadata.space}/${metadata.name}

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
registry = CardRegistry("${registryType.toLowerCase()}")
card = registry.load_card(uid="${metadata.uid}")
\`\`\`
`,

  [RegistryType.Experiment]: (
    metadata: CardMetadata,
    registryType: string
  ): string => `# ExperimentCard for ${metadata.space}/${metadata.name}

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
registry = CardRegistry("${registryType.toLowerCase()}")
card = registry.load_card(uid="${metadata.uid}")
\`\`\`
`,

  [RegistryType.Prompt]: (
    metadata: CardMetadata,
    registryType: string
  ): string => `# Prompt Card for ${metadata.space}/${metadata.name}

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
registry = CardRegistry("${registryType.toLowerCase()}")
card = registry.load_card(uid="${metadata.uid}")
\`\`\`
`,
};

/**
 * Generic function to generate readme content based on registry type
 */
export function generateReadmeContent(
  registryType: RegistryType,
  metadata: CardMetadata,
  readme: ReadmeData
): string {
  if (readme.exists && readme.readme) {
    return readme.readme;
  }

  const templateFn = readmeTemplates[registryType];
  if (!templateFn) {
    throw new Error(`Unsupported registry type: ${registryType}`);
  }

  return templateFn(metadata, registryType);
}
