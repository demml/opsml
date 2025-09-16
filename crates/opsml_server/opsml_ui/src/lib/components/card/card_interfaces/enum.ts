import type { DataCard } from "./datacard";
import type { ModelCard } from "./modelcard";
import type { PromptCard } from "./promptcard";
import type { ExperimentCard } from "./experimentcard";
import type { ServiceCard } from "./servicecard";

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
