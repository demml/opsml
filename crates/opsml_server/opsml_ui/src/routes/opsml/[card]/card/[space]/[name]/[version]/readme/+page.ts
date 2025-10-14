import type { PageLoad } from "./$types";
import { generateReadmeContent } from "$lib/components/readme/readmeGenerator";

export const load: PageLoad = async ({ parent }) => {
  const { metadata, registryType, readme } = await parent();

  const content = generateReadmeContent(registryType, metadata, readme);

  return {
    metadata,
    content,
  };
};
