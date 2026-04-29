import { RegistryType } from "$lib/utils";
import type { Prompt } from "$lib/components/agent/types";
import type { DriftProfileUri } from "$lib/components/scouter/types";
import type { AgentEvalProfile } from "$lib/components/scouter/agent/types";

export interface PromptCardMetadata {
  experimentcard_uid?: string;
  auditcard_uid?: string;
  drift_profile_uri_map?: Record<string, DriftProfileUri>;
}

export interface PromptCard {
  prompt: Prompt;
  name: string;
  space: string;
  version: string;
  uid: string;
  tags: string[];
  metadata: PromptCardMetadata;
  registry_type: RegistryType.Prompt;
  app_env: string;
  created_at: string; // ISO datetime string
  is_card: boolean;
  opsml_version: string;
  eval_profile?: AgentEvalProfile;
}

export function isPromptCard(obj: unknown): obj is PromptCard {
  if (typeof obj !== "object" || obj === null) {
    return false;
  }

  const card = obj as Partial<PromptCard>;
  return (
    card.registry_type === RegistryType.Prompt &&
    typeof card.prompt === "object" &&
    card.prompt !== null &&
    typeof card.name === "string" &&
    typeof card.space === "string" &&
    typeof card.version === "string" &&
    typeof card.uid === "string"
  );
}
