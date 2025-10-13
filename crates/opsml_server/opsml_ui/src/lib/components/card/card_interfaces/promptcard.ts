import { RegistryType } from "$lib/utils";
import type { DriftType } from "../monitoring/types";
import type { Prompt } from "$lib/components/genai/types";

export interface DriftProfileUri {
  root_dir: string;
  uri: string;
  drift_type: DriftType;
}

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
}
