export const ssr = false;

import { getHardwareMetrics } from "$lib/components/card/experiment/util";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent }) => {
  const { metadata } = await parent();

  // get metric names, parameters
  let hardwareMetrics = await getHardwareMetrics(metadata.uid);

  return { hardwareMetrics };
};
