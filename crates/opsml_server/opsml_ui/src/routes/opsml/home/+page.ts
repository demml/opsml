import { getRecentCards } from "$lib/components/home/utils";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({}) => {
  await validateUserOrRedirect();

  let cards = await getRecentCards();

  return { cards: cards };
};
