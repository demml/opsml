export const ssr = false;

import type { LayoutLoad } from "./$types";
import { getRegistryPath, RegistryType } from "$lib/utils";
import { redirect } from "@sveltejs/kit";
import { isPromptCard } from "$lib/components/card/card_interfaces/promptcard";
import { buildMockAgentPromptCards } from "$lib/components/mock/opsmlMockData";

export const load: LayoutLoad = async ({ parent }) => {
  const parentData = await parent();
  const {
    registryType,
    metadata,
    promptCardsWithEval,
    devMockEnabled,
  } = parentData;

  const mockMode = Boolean(devMockEnabled);

  // ── Agent registry: collect all associated prompt cards that have eval profiles ──
  if (registryType === RegistryType.Agent) {
    if (promptCardsWithEval.length === 0) {
      if (mockMode) {
        return {
          registryType,
          metadata,
          promptCardsWithEval: buildMockAgentPromptCards(metadata.space),
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
  // isPromptCard normalizes registry_type to lowercase before comparing, so it
  // correctly handles the PascalCase "Prompt" emitted by Rust's #[derive(Serialize)].
  if (!isPromptCard(metadata)) {
    throw redirect(
      303,
      `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${metadata.name}/${metadata.version}/card`,
    );
  }

  const eval_profile = metadata.eval_profile;

  if (!eval_profile) {
    if (mockMode) {
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
