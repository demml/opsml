import type { PageServerLoad } from "./$types";
import { getRawFile } from "$lib/server/card/files/utils";
import { buildMockRawFile } from "$lib/components/mock/opsmlMockData";
import { isDevMockEnabled } from "$lib/server/mock/mode";

export const load: PageServerLoad = async ({ parent, url, fetch, cookies }) => {
  const { registryType, metadata } = await parent();
  const useMockFallback = isDevMockEnabled(cookies);
  const viewPath = (url as URL).searchParams.get("path") as string;

  if (useMockFallback) {
    return {
      rawFile: buildMockRawFile(viewPath),
      viewPath,
      splitPath: viewPath.split("/"),
      mockMode: true,
    };
  }

  try {
    const rawFile = await getRawFile(fetch, viewPath, metadata.uid, registryType);
    const splitPath = viewPath.split("/");

    return { rawFile, viewPath, splitPath, mockMode: false };
  } catch (error) {
    if (!useMockFallback) {
      throw error;
    }

    return {
      rawFile: buildMockRawFile(viewPath),
      viewPath,
      splitPath: viewPath.split("/"),
      mockMode: true,
    };
  }
};
