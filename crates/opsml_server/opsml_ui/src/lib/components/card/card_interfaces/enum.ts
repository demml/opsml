import type { DataCard } from "./datacard";
import type { ModelCard } from "./modelcard";
import type { PromptCard } from "./promptcard";
import type { ExperimentCard } from "./experimentcard";
import type { ServiceCard } from "./servicecard";
import { isPromptCard } from "./promptcard";

export type CardMetadata =
  | { Data: DataCard }
  | { Model: ModelCard }
  | { Prompt: PromptCard }
  | { Experiment: ExperimentCard };

export type AnyCard =
  | DataCard
  | ModelCard
  | PromptCard
  | ExperimentCard
  | ServiceCard;

/**
 * Given a PromptCard or ServiceCard/AgentCard, returns the eval profile config
 * for PromptCards, or the card's uid for ServiceCard/AgentCard.
 */
export function getEvalProfileOrUid(card: PromptCard | ServiceCard): string {
  if (isPromptCard(card)) {
    return card.eval_profile?.config.uid || "";
  }
  return card.uid;
}
