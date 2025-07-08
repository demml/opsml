export const ssr = false;

import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent }) => {
  const { metadata, registry, registryPath } = await parent();

  return { metadata, registry, registryPath };
};
