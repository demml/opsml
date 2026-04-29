import type { LayoutServerLoad } from "./$types";
import { loadCardLayout } from "$lib/server/card/layout";
import { RegistryType } from "$lib/utils";
import { isDevMockEnabled } from "$lib/server/mock/mode";
import type { PromptCard } from "$lib/components/card/card_interfaces/promptcard";

// @ts-ignore
export const load: LayoutServerLoad = async ({ params, parent, fetch, cookies }) => {
  const { registryType } = await parent();
  const { space, name, version } = params;
  const useMockFallback = isDevMockEnabled(cookies);

  const cardLayout = await loadCardLayout(
    registryType as RegistryType,
    space,
    name,
    version,
    fetch,
    useMockFallback,
  );

  if (registryType === RegistryType.Prompt) {
    const promptCard = cardLayout.metadata as PromptCard;
    const showEvalTab = !!promptCard.eval_profile || useMockFallback;
    return { ...cardLayout, promptCardsWithEval: [], showEvalTab };
  }

  return cardLayout;
};
