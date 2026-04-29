import { getExperimentFigures } from "$lib/server/experiment/utils";
import { buildMockFigures } from "$lib/components/mock/opsmlMockData";
import { isDevMockEnabled } from "$lib/server/mock/mode";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ parent, fetch, cookies }) => {
  const { metadata } = await parent();
  const useMockFallback = isDevMockEnabled(cookies);

  try {
    let experimentFigures = await getExperimentFigures(
      fetch,
      metadata.uid,
      metadata.space,
      metadata.name,
      metadata.version
    );

    if (useMockFallback && experimentFigures.length === 0) {
      return { figures: buildMockFigures(), mockMode: true };
    }

    return { figures: experimentFigures, mockMode: false };
  } catch (error) {
    if (!useMockFallback) {
      throw error;
    }

    return { figures: buildMockFigures(), mockMode: true };
  }
};
