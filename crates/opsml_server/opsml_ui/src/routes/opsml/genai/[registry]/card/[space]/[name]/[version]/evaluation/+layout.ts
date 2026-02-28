export const ssr = false;

import type { LayoutLoad } from "./$types";
import { getRegistryPath, RegistryType } from "$lib/utils";
import { redirect } from "@sveltejs/kit";
import { isPromptCard } from "$lib/components/card/card_interfaces/promptcard";
import type { PromptCard } from "$lib/components/card/card_interfaces/promptcard";
import type {
  ServiceCard,
  Card,
} from "$lib/components/card/card_interfaces/servicecard";
import { RoutePaths } from "$lib/components/api/routes";

/** Fetch a single prompt card's full metadata using a relative-path fetch call. */
async function fetchPromptCardMetadata(
  fetchFn: typeof globalThis.fetch,
  card: Card,
): Promise<PromptCard | null> {
  try {
    const params = new URLSearchParams({
      name: card.name,
      space: card.space,
      version: card.version,
      registry_type: RegistryType.Prompt,
    });

    const resp = await fetchFn(`${RoutePaths.METADATA}?${params.toString()}`);
    if (!resp.ok) return null;

    const data = await resp.json();
    return isPromptCard(data) ? (data as PromptCard) : null;
  } catch {
    return null;
  }
}

export const load: LayoutLoad = async ({ parent, fetch }) => {
  const parentData = await parent();
  const { registryType, metadata } = parentData;

  // ── Agent registry: collect all associated prompt cards that have eval profiles ──
  if (registryType === RegistryType.Agent) {
    const serviceCard = metadata as ServiceCard;
    const associatedCards: Card[] = serviceCard.cards?.cards ?? [];

    console.log(`Cards: ${JSON.stringify(associatedCards)}`); // Debug log

    // Fetch metadata for all associated prompt cards in parallel
    const promptCardResults = await Promise.all(
      associatedCards
        .filter((c) => c.registry_type === "Prompt")
        .map((c) => fetchPromptCardMetadata(fetch, c)),
    );

    console.log(
      `Successfully fetched metadata for ${promptCardResults.filter(Boolean).length} prompt cards`,
    ); // Debug log

    // Collect prompt cards that have eval profiles
    const promptCardsWithEval: PromptCard[] = promptCardResults.filter(
      (card): card is PromptCard => card !== null && !!card.eval_profile,
    );

    if (promptCardsWithEval.length === 0) {
      throw redirect(
        303,
        `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${metadata.name}/${metadata.version}/card`,
      );
    }

    return {
      registryType,
      metadata,
      // Agent-specific: list of prompt cards with their eval profiles
      promptCardsWithEval,
      // Not used for agents but kept for type compatibility with prompt route
      eval_profile: undefined,
    };
  }

  // ── Prompt registry: existing single-card evaluation flow ──
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
    promptCardsWithEval: undefined,
  };
};
