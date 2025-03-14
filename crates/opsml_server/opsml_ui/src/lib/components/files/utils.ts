import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import { RegistryType } from "$lib/utils";
import type { CardQueryArgs } from "../api/schema";
import type { ListFileInfoResponse } from "./types";
import { type FileInfo, type DirectoryInfo } from "./types";

export function separateFiles(files: FileInfo[]): {
  currentPathFiles: FileInfo[];
  directories: DirectoryInfo[];
} {
  const currentPathFiles: FileInfo[] = [];
  const directoriesMap: Map<string, string> = new Map();

  files.forEach((file) => {
    const filePath = file.name;
    const firstSlashIndex = filePath.indexOf("/");
    if (firstSlashIndex === -1) {
      // File is in the current path
      currentPathFiles.push(file);
    } else {
      // File is in a nested directory
      const directoryName = filePath.slice(0, firstSlashIndex);
      const existingTimestamp = directoriesMap.get(directoryName);
      if (
        !existingTimestamp ||
        new Date(file.created) > new Date(existingTimestamp)
      ) {
        directoriesMap.set(directoryName, file.created);
      }
    }
  });

  // Convert Map to Array and sort directories alphabetically
  const directories: DirectoryInfo[] = Array.from(directoriesMap.entries())
    .map(([name, created]) => ({ name, created }))
    .sort((a, b) => a.name.localeCompare(b.name));

  // Sort currentPathFiles alphabetically by name
  currentPathFiles.sort((a, b) => a.name.localeCompare(b.name));

  return { currentPathFiles, directories };
}

export async function getFileInfo(path: string): Promise<ListFileInfoResponse> {
  const params = {
    path: path,
  };

  const response = await opsmlClient.get(RoutePaths.FILE_INFO, params);
  return (await response.json()) as ListFileInfoResponse;
}
