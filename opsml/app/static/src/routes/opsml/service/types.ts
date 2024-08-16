import type { ComponentType } from "svelte";

export interface DraggableItem {
  id: string;
  content: string;
  component: ComponentType;
}
