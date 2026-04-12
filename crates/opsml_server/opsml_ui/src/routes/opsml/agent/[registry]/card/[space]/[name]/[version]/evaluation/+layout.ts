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
import { dev } from "$app/environment";

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
  const { registryType, metadata, promptCardsWithEval, settings } = parentData;

  const mockMode = dev && !settings?.scouter_enabled;

  // ── Agent registry: collect all associated prompt cards that have eval profiles ──
  if (registryType === RegistryType.Agent) {
    if (promptCardsWithEval.length === 0) {
      if (dev) {
        const { buildMockAgentEvalProfile } =
          await import("$lib/components/scouter/evaluation/mockData");
        const mockProfile = buildMockAgentEvalProfile();
        const mockPromptCard = {
          name: "mock-intent-classifier",
          space: metadata.space,
          version: "1.0.0",
          uid: "mock-prompt-uid-001",
          tags: ["mock"],
          metadata: {} as any,
          registry_type: "Prompt",
          app_env: "development",
          created_at: new Date().toISOString(),
          is_card: true,
          opsml_version: "1.0.0",
          eval_profile: mockProfile,
          prompt: {} as any,
        } as any;

        return {
          registryType,
          metadata,
          promptCardsWithEval: [mockPromptCard],
          eval_profile: undefined,
          mockMode: true,
        };
      }
      throw redirect(
        303,
        `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${metadata.name}/${metadata.version}/card`,
      );
    }

    return {
      registryType,
      metadata,
      promptCardsWithEval,
      eval_profile: undefined,
      mockMode,
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
    if (dev) {
      const { buildMockAgentEvalProfile } =
        await import("$lib/components/scouter/evaluation/mockData");
      return {
        registryType,
        metadata,
        eval_profile: buildMockAgentEvalProfile(),
        promptCardsWithEval,
        mockMode: true,
      };
    }
    throw redirect(
      303,
      `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${metadata.name}/${metadata.version}/card`,
    );
  }

  return {
    registryType,
    metadata,
    eval_profile,
    promptCardsWithEval,
    mockMode,
  };
};
