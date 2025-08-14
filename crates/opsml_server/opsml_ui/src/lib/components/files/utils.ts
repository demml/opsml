import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import type { FileTreeResponse, RawFile, RawFileRequest } from "./types";
import { AcceptableSuffix } from "./types";
import Highlight, { LineNumbers } from "svelte-highlight";
import json from "svelte-highlight/languages/json";
import python from "svelte-highlight/languages/python";
import yaml from "svelte-highlight/languages/yaml";
import sql from "svelte-highlight/languages/sql";
import { userStore } from "../user/user.svelte";
import type { RegistryType } from "$lib/utils";

export async function getFileTree(path: string): Promise<FileTreeResponse> {
  const params = {
    path: path,
  };

  const response = await opsmlClient.get(
    RoutePaths.FILE_TREE,
    params,
    userStore.jwt_token
  );
  return (await response.json()) as FileTreeResponse;
}

export function timeAgo(timestamp: string): string {
  let date: Date;

  if (/^\d+$/.test(timestamp)) {
    date = new Date(
      timestamp.length === 13 ? parseInt(timestamp) : parseInt(timestamp) * 1000
    );
  } else {
    date = parseRFC3339Variant(timestamp);
  }

  if (isNaN(date.getTime())) {
    return "invalid date";
  }

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

function parseRFC3339Variant(timestamp: string): Date {
  // try native parsing (handles standard ISO 8601/RFC 3339)
  let date = new Date(timestamp);
  if (!isNaN(date.getTime())) {
    return date;
  }

  // Normalize RFC 3339 variants to standard format
  let normalized = timestamp.trim();

  // Handle Google style format: "2025-07-09 15:26:44.373 +00:00:00"
  // 1. Replace space before date/time separator with 'T'
  normalized = normalized.replace(
    /^(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})/,
    "$1T$2"
  );

  // 2. Remove extra space before timezone offset
  normalized = normalized.replace(/\s+([+-]\d{2}:\d{2}(?::\d{2})?)$/, "$1");

  // 3. Remove extra seconds from timezone offset (+00:00:00 -> +00:00)
  normalized = normalized.replace(/([+-]\d{2}:\d{2}):\d{2}$/, "$1");

  // Try parsing the normalized timestamp
  date = new Date(normalized);
  if (!isNaN(date.getTime())) {
    return date;
  }

  // Fallback: assume UTC if no timezone specified
  if (!/[+-]\d{2}:?\d{2}$|Z$/.test(normalized)) {
    const utcTimestamp = normalized + "Z";
    date = new Date(utcTimestamp);
    if (!isNaN(date.getTime())) {
      return date;
    }
  }

  // Return invalid date if all parsing attempts fail
  return new Date(NaN);
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
  registry_type: RegistryType
): Promise<RawFile> {
  const body: RawFileRequest = {
    path: path,
    uid: uid,
    registry_type: registry_type,
  };

  const response = await opsmlClient.post(
    RoutePaths.FILE_CONTENT,
    body,
    userStore.jwt_token
  );
  return (await response.json()) as RawFile;
}

function splitViewPath(path: string): string[] {
  let splitPath = path.split("/");
  return splitPath;
}

export function formatJson(jsonString: string): string {
  let newJson = JSON.stringify(JSON.parse(jsonString), null, 2);
  return newJson;
}
