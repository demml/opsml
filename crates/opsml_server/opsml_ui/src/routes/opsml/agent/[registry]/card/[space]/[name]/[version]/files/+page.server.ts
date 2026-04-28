import type { PageServerLoad } from "./$types";
import { getFileTree, getRawFile } from "$lib/server/card/files/utils";
import { getRegistryTableName } from "$lib/utils";
import {
  buildMockFileTree,
  buildMockRawFile,
} from "$lib/components/mock/opsmlMockData";
import { isDevMockEnabled } from "$lib/server/mock/mode";

export const load: PageServerLoad = async ({ parent, fetch, url, cookies }) => {
  const { metadata, registryType } = await parent();
  const useMockFallback = isDevMockEnabled(cookies);

  const tableName = getRegistryTableName(registryType);
  const basePath = `${tableName}/${metadata.space}/${metadata.name}/v${metadata.version}`;
  const viewPath = url.searchParams.get("view");

  try {
    const fileTree = await getFileTree(fetch, basePath);

    let rawFile = null;
    if (viewPath) {
      rawFile = await getRawFile(fetch, viewPath, metadata.uid, registryType);
    }

    if (useMockFallback && fileTree.files.length === 0) {
      return {
        fileTree: buildMockFileTree(basePath),
        basePath,
        viewPath,
        rawFile: viewPath ? buildMockRawFile(viewPath) : null,
        mockMode: true,
      };
    }

    return { fileTree, basePath, viewPath, rawFile, mockMode: false };
  } catch (error) {
    if (!useMockFallback) {
      throw error;
    }

    return {
      fileTree: buildMockFileTree(basePath),
      basePath,
      viewPath,
      rawFile: viewPath ? buildMockRawFile(viewPath) : null,
      mockMode: true,
    };
  }
};
