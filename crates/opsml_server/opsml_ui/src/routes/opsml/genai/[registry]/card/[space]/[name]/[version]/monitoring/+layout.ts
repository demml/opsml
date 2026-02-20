export const ssr = false;

import type { LayoutLoad } from "./$types";
import { getRegistryPath } from "$lib/utils";
import { redirect } from "@sveltejs/kit";
import { isPromptCard } from "$lib/components/card/card_interfaces/promptcard";

export const load: LayoutLoad = async ({ parent, fetch, url }) => {
  const parentData = await parent();
  const { registryType, metadata } = parentData;

  // only prompt profile available for prompt registry, if not prompt registry, redirect to card page
  if (!isPromptCard(metadata)) {
    throw redirect(
      303,
      `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${metadata.name}/${metadata.version}/card`,
    );
  }

  const eval_profile = metadata.eval_profile;

  if (!eval_profile) {
    throw redirect(
      303,
      `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${metadata.name}/${metadata.version}/card`,
    );
  }

  return {
    registryType,
    metadata,
    eval_profile,
  };
};
