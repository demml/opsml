import { getRecentCards } from "$lib/components/home/utils";
import { opsmlClient } from "$lib/components/api/client.svelte";
import type { PageLoad } from "./$types";

export const load: PageLoad = async () => {
  await opsmlClient.validateAuth();

  let cards = await getRecentCards();
  return { cards: cards };
};
