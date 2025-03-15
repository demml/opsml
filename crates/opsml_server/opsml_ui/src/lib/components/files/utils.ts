import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import type { FileTreeResponse, RawFile } from "./types";
import { AcceptableSuffix } from "./types";

export async function getFileTree(path: string): Promise<FileTreeResponse> {
  const params = {
    path: path,
  };

  const response = await opsmlClient.get(RoutePaths.FILE_TREE, params);
  return (await response.json()) as FileTreeResponse;
}

export function timeAgo(timestamp: string): string {
  const date = new Date(parseInt(timestamp) * 1000); // Convert to milliseconds
  const now = new Date();
  const secondsAgo = Math.floor((now.getTime() - date.getTime()) / 1000);

  const intervals = [
    { label: "year", seconds: 31536000 },
    { label: "month", seconds: 2592000 },
    { label: "day", seconds: 86400 },
    { label: "hour", seconds: 3600 },
    { label: "minute", seconds: 60 },
    { label: "second", seconds: 1 },
  ];

  for (const interval of intervals) {
    const count = Math.floor(secondsAgo / interval.seconds);
    if (count >= 1) {
      return `${count} ${interval.label}${count !== 1 ? "s" : ""} ago`;
    }
  }

  return "just now";
}

export function formatBytes(bytes: number): string {
  const units = ["bytes", "kb", "Mb", "Gb", "Tb"];
  let unitIndex = 0;

  while (bytes >= 1000 && unitIndex < units.length - 1) {
    bytes /= 1000;
    unitIndex++;
  }

  return `${bytes.toFixed(1)} ${units[unitIndex]}`;
}

export function isAcceptableSuffix(suffix: string): boolean {
  return Object.values(AcceptableSuffix).includes(
    suffix.toLowerCase() as AcceptableSuffix
  );
}

export async function getRawFile(
  path: string,
  uid: string,
  registry_type: string
): Promise<RawFile> {
  const body = {
    path: path,
    uid: uid,
    registry_type: registry_type,
  };

  const response = await opsmlClient.post(RoutePaths.FILE_CONTENT, body);
  return (await response.json()) as RawFile;
}

function splitViewPath(path: string): string[] {
  let splitPath = path.split("/");
  return splitPath;
}
