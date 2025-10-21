import { getRegistryPath, RegistryType } from "$lib/utils";
import { type Card } from "$lib/components/home/types";

export function getBgColor(): string {
  const classes = [
    "bg-primary-500",
    "bg-secondary-500",
    "bg-tertiary-500",
    "bg-success-500",
    "bg-warning-500",
    "bg-error-500",
  ];
  const randomIndex = Math.floor(Math.random() * classes.length);
  return classes[randomIndex];
}

export function resolveCardPath(card: Card): string {
  let registry = card.type.toLowerCase();

  if (registry === "prompt" || registry === "mcp" || registry === "agent") {
    return `/opsml/genai/${registry}/card/${card.data.space}/${card.data.name}/${card.data.version}/card`;
  }
  return `/opsml/${registry}/card/${card.data.space}/${card.data.name}/${card.data.version}/card`;
}

export function resolveCardPathFromArgs(
  registry: RegistryType,
  space: string,
  name: string,
  version: string
): string {
  return `/opsml/${getRegistryPath(
    registry
  )}/card/${space}/${name}/${version}/card`;
}
