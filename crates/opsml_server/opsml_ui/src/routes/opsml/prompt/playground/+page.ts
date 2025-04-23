export const ssr = false;

import { setupRegistryPage } from "$lib/components/card/utils";
import { opsmlClient } from "$lib/components/api/client.svelte";
import { RegistryType } from "$lib/utils";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ url }) => {
  return { registry_type: RegistryType.Prompt };
};
