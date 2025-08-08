export const ssr = false;

import { getHardwareMetrics } from "$lib/components/card/experiment/util";
import type { PageLoad } from "./$types";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

export const load: PageLoad = async ({ parent }) => {
  await validateUserOrRedirect();
  const { metadata } = await parent();

  // get metric names, parameters
  let hardwareMetrics = await getHardwareMetrics(metadata.uid);

  return { hardwareMetrics };
};
