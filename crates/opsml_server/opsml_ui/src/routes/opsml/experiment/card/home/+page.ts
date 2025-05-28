export const ssr = false;

import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent }) => {
  const { metadata, registry, readme, registryPath } = await parent();

  return { metadata, registry, readme, registryPath };
};
