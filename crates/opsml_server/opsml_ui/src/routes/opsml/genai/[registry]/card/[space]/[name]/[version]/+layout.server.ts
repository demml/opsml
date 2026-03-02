import type { LayoutServerLoad } from "./$types";
import { loadCard, loadCardLayout } from "$lib/server/card/layout";
import { RegistryType } from "$lib/utils";
import type {
  Card,
  ServiceCard,
} from "$lib/components/card/card_interfaces/servicecard";
import type { PromptCard } from "$lib/components/card/card_interfaces/promptcard";

async function setup_agent_layout(
  card: ServiceCard,
  fetch: typeof globalThis.fetch,
): Promise<PromptCard[]> {
  const associatedCards: Card[] = card.cards?.cards ?? [];

  const promptCardResults = (await Promise.all(
    associatedCards
      .filter((c) => c.registry_type === "Prompt")
      .map((c) =>
        loadCard(RegistryType.Prompt, c.space, c.name, c.version, fetch),
      ),
  )) as (PromptCard | null)[];

  const promptCardsWithEval: PromptCard[] = promptCardResults.filter(
    (card): card is PromptCard => card !== null && !!card.eval_profile,
  );

  return promptCardsWithEval;
}

// @ts-ignore
export const load: LayoutServerLoad = async ({ params, parent, fetch }) => {
  const { registryType } = await parent();
  const { space, name, version } = params;

  let genAIRegistryType = registryType as RegistryType;

  let cardLayout = await loadCardLayout(
    genAIRegistryType,
    space,
    name,
    version,
    fetch,
  );

  if (genAIRegistryType === RegistryType.Agent) {
    // load all cards for service and find prompt cards with eval profiles
    const serviceCard = cardLayout.metadata as ServiceCard;
    const promptCardsWithEval = await setup_agent_layout(serviceCard, fetch);
    const showEvalTab = promptCardsWithEval.length > 0;

    // add to layout data
    return { ...cardLayout, promptCardsWithEval, showEvalTab };
  }

  // if registry is prompt, check if card has eval profile to determine whether to show eval tab in layout
  if (genAIRegistryType === RegistryType.Prompt) {
    const promptCard = cardLayout.metadata as PromptCard;
    const showEvalTab = !!promptCard.eval_profile;

    return { ...cardLayout, promptCardsWithEval: [], showEvalTab };
  }

  return { ...cardLayout, promptCardsWithEval: [], showEvalTab: false };
};
