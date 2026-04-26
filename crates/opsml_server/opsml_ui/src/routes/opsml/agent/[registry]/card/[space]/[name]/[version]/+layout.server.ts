import type { LayoutServerLoad } from "./$types";
import { loadCard, loadCardLayout } from "$lib/server/card/layout";
import { RegistryType } from "$lib/utils";
import { isDevMockEnabled } from "$lib/server/mock/mode";
import type {
  Card,
  ServiceCard,
} from "$lib/components/card/card_interfaces/servicecard";
import type { PromptCard } from "$lib/components/card/card_interfaces/promptcard";
import { buildMockAgentPromptCards } from "$lib/components/mock/opsmlMockData";

async function setup_agent_layout(
  card: ServiceCard,
  fetch: typeof globalThis.fetch,
  useMockFallback: boolean,
): Promise<PromptCard[]> {
  const associatedCards: Card[] = card.cards?.cards ?? [];

  if (useMockFallback) {
    return buildMockAgentPromptCards(card.space, associatedCards).filter(
      (card) => !!card.eval_profile,
    );
  }

  const promptCardResults = (await Promise.all(
    associatedCards
      .filter((c) => c.registry_type.toLowerCase() === "prompt")
      .map((c) =>
        loadCard(
          RegistryType.Prompt,
          c.space,
          c.name,
          c.version,
          fetch,
          useMockFallback,
        ),
      ),
  )) as (PromptCard | null)[];

  const promptCardsWithEval: PromptCard[] = promptCardResults.filter(
    (card): card is PromptCard => card !== null && !!card.eval_profile,
  );

  return promptCardsWithEval;
}

export const load: LayoutServerLoad = async ({ params, parent, fetch, cookies }) => {
  const { registryType } = await parent();
  const { space, name, version } = params;
  const useMockFallback = isDevMockEnabled(cookies);

  const genAIRegistryType = registryType as RegistryType;

  const cardLayout = await loadCardLayout(
    genAIRegistryType,
    space,
    name,
    version,
    fetch,
    useMockFallback,
  );

  if (genAIRegistryType === RegistryType.Agent) {
    // load all cards for service and find prompt cards with eval profiles
    const serviceCard = cardLayout.metadata as ServiceCard;
    const promptCardsWithEval = await setup_agent_layout(
      serviceCard,
      fetch,
      useMockFallback,
    );
    const showEvalTab = promptCardsWithEval.length > 0 || useMockFallback;

    // add to layout data
    return { ...cardLayout, promptCardsWithEval, showEvalTab };
  }

  // if registry is prompt, check if card has eval profile to determine whether to show eval tab in layout
  if (genAIRegistryType === RegistryType.Prompt) {
    const promptCard = cardLayout.metadata as PromptCard;
    const showEvalTab = !!promptCard.eval_profile || useMockFallback;

    return { ...cardLayout, promptCardsWithEval: [], showEvalTab };
  }

  return { ...cardLayout, promptCardsWithEval: [], showEvalTab: false };
};
