import type { RegistryType } from "$lib/utils";

export interface CardQueryArgs {
  uid?: string;
  name?: string;
  space?: string;
  version?: string;
  registry_type: RegistryType;
  limit?: number;
  sort_by_timestamp?: boolean;
}

export interface ReadMeArgs {
  name: string;
  space: string;
  registry_type: RegistryType;
  readme: string;
}
