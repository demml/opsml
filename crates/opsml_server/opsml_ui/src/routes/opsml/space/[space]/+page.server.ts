import { getSpace } from "$lib/server/space/utils";
import type { PageServerLoad } from "./$types";
import { getRecentCards } from "$lib/components/home/utils.server";
import {
  buildMockSpaceRecord,
  isRecentCardsEmpty,
  mergeRecentCardsWithMock,
} from "$lib/components/mock/opsmlMockData";
import { isDevMockEnabled } from "$lib/server/mock/mode";

export const load: PageServerLoad = async ({ params, fetch, cookies }) => {
  const useMockFallback = isDevMockEnabled(cookies);

  try {
    let spaceRecord = await getSpace(fetch, params.space);
    let recentCards = await getRecentCards(fetch, params.space);

    if (useMockFallback && isRecentCardsEmpty(recentCards)) {
      return {
        spaceRecord:
          spaceRecord.description || spaceRecord.space
            ? spaceRecord
            : buildMockSpaceRecord(params.space),
        recentCards: mergeRecentCardsWithMock(recentCards, params.space),
        mockMode: true,
      };
    }

    return { spaceRecord, recentCards, mockMode: false };
  } catch {
    if (useMockFallback) {
      return {
        spaceRecord: buildMockSpaceRecord(params.space),
        recentCards: mergeRecentCardsWithMock(
          {
            modelcards: [],
            datacards: [],
            experimentcards: [],
            promptcards: [],
          },
          params.space,
        ),
        mockMode: true,
      };
    }

    throw new Error(`Failed to load space ${params.space}`);
  }
};
