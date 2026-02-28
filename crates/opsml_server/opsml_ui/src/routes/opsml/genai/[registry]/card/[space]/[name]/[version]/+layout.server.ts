import type { LayoutServerLoad } from "./$types";
import { loadCard, loadCardLayout } from "$lib/server/card/layout";
import { RegistryType } from "$lib/utils";
import type {
  Card,
  ServiceCard,
} from "$lib/components/card/card_interfaces/servicecard";
import type { PromptCard } from "$lib/components/card/card_interfaces/promptcard";

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
    // load all cards
    const serviceCard = cardLayout.metadata as ServiceCard;
    const associatedCards: Card[] = serviceCard.cards?.cards ?? [];

    const promptCardResults = (await Promise.all(
      associatedCards
        .filter((c) => c.registry_type === "Prompt")
        .map((c) =>
          loadCard(RegistryType.Prompt, c.space, c.name, c.version, fetch),
        ),
    )) as (PromptCard | null)[];

    // iterate over
    const promptCardsWithEval: PromptCard[] = promptCardResults.filter(
      (card): card is PromptCard => card !== null && !!card.eval_profile,
    );
  }

  return { ...cardLayout };
};
