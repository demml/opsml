import { getExperimentFigures } from "$lib/server/experiment/utils";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ parent, fetch }) => {
  const { metadata } = await parent();

  // get metric names, parameters
  let experimentFigures = await getExperimentFigures(
    fetch,
    metadata.uid,
    metadata.space,
    metadata.name,
    metadata.version
  );

  return { figures: experimentFigures };
};
