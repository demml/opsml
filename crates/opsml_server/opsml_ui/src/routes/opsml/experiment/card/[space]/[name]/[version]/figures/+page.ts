export const ssr = false;

import {
  getExperimentFigures,
  getHardwareMetrics,
} from "$lib/components/card/experiment/util";
import type { PageLoad } from "./$types";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

export const load: PageLoad = async ({ parent }) => {
  await validateUserOrRedirect();
  const { metadata } = await parent();

  // get metric names, parameters
  let experimentFigures = await getExperimentFigures(metadata.uid);

  console.log(experimentFigures);

  return { experimentFigures };
};
