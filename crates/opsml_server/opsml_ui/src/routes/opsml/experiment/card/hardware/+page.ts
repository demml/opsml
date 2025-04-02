export const ssr = false;

import { opsmlClient } from "$lib/components/api/client.svelte";
import { getHardwareMetrics } from "$lib/components/card/experiment/util";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent }) => {
  await opsmlClient.validateAuth(true);

  const { metadata } = await parent();

  // get metric names, parameters
  let hardwareMetrics = await getHardwareMetrics(metadata.uid);

  console.log("hardwareMetrics", hardwareMetrics);

  return { hardwareMetrics };
};
