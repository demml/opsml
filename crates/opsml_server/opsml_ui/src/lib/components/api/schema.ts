import type { RegistryType } from "$lib/utils";

export interface CardQueryArgs {
  uid?: string;
  name?: string;
  repository?: string;
  version?: string;
  registry_type: RegistryType;
  limit?: number;
}

export interface ReadMeArgs {
  name: string;
  repository: string;
  registry_type: RegistryType;
  readme: string;
}
