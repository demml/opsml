export const ssr = false;

import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent }) => {
  const { metadata, registryType, readme, registryPath } = await parent();

  return { metadata, registryType, readme, registryPath };
};
