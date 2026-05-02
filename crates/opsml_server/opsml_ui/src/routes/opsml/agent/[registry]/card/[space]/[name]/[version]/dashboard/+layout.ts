export const ssr = false;

import type { LayoutLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import { getRegistryPath, RegistryType } from '$lib/utils';
import type { PromptCard } from '$lib/components/card/card_interfaces/promptcard';

/**
 * Dashboard route serves both AgentCard and PromptCard registries.
 *
 * - Agent: scoped by `service_name = "{space}:{name}"` (matches `ServiceInfo::namespace()`).
 * - Prompt: scoped by `entity_id = eval_profile.config.uid`. Redirects back to
 *   the card overview when the prompt has no eval profile (nothing to scope by).
 */
export const load: LayoutLoad = async ({ parent }) => {
  const parentData = await parent();
  const { metadata, registryType, devMockEnabled } = parentData as {
    metadata: PromptCard | { space: string; name: string; version: string };
    registryType: RegistryType;
    devMockEnabled?: boolean;
  };

  const mockMode = Boolean(devMockEnabled);

  // Prompt scope requires an eval profile. Without one there is no entity_id
  // to query and the dashboard would render empty.
  if (registryType === RegistryType.Prompt) {
    const promptCard = metadata as PromptCard;
    if (!promptCard.eval_profile && !mockMode) {
      throw redirect(
        303,
        `/opsml/${getRegistryPath(registryType)}/card/${promptCard.space}/${promptCard.name}/${promptCard.version}/card`,
      );
    }
  }

  return {
    metadata,
    registryType,
    mockMode,
  };
};
