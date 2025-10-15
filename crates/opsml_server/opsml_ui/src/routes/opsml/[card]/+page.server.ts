import { setupRegistryPage } from "$lib/server/card/utils";
import { getRegistryFromString, RegistryType } from "$lib/utils";
import { redirect } from "@sveltejs/kit";
import type { PageServerLoad, EntryGenerator } from "./$types";

export const entries: EntryGenerator = () => {
  return [
    { card: "model" },
    { card: "data" },
    { card: "experiment" },
    { card: "service" },
  ];
};

export const load: PageServerLoad = async ({ parent, fetch }) => {
  let { registryType } = await parent();

  if (!registryType) {
    throw redirect(307, "/opsml/home");
  }

  let registryPage = await setupRegistryPage(
    registryType,
    undefined,
    undefined,
    fetch
  );

  return {
    page: registryPage,
    selectedSpace: undefined,
    selectedName: undefined,
  };
};
