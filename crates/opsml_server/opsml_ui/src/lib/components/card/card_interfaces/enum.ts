import type { DataCard } from "./datacard";
import type { ModelCard } from "./modelcard";
import type { PromptCard } from "./promptcard";
import type { ExperimentCard } from "./experimentcard";

export type CardMetadata =
  | { Data: DataCard }
  | { Model: ModelCard }
  | { Prompt: PromptCard }
  | { Experiment: ExperimentCard };
