<script lang="ts">

    import { calculateTimeBetween, RegistryType } from "$lib/utils";
    import {CircuitBoard, Clock, Tag } from 'lucide-svelte';
  import { resolveCardPathFromArgs } from "./utils";
  
    let {
      name,
      space,
      version,
      registry,
      updated_at,
      bgColor
    } = $props<{
      name: string;
      space: string;
      version: string;
      registry: RegistryType;
      updated_at: string;
      bgColor: string;
    }>();

    function resolveUrl(): string{
      let path = resolveCardPathFromArgs(registry, space, name, version);
      return path;
    }

    let cardUrl = resolveUrl();

  </script>
  
  <a 
    class="w-full max-w-96 h-auto p-3 text-black rounded-lg shadow border-2 border-black {bgColor} hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none overflow-scroll" 
    href={cardUrl}
    data-sveltekit-preload-data="hover"
    >
    <div class="flex items-center justify-start gap-2 text-smd">
      <div class="ml-1">
        <CircuitBoard color="#5948a3" />
      </div>
      <div><h4 class="truncate font-bold">{space}/{name}</h4></div>
    </div>
 
    <div class="flex items-center justify-start gap-2 overflow-hidden whitespace-nowrap text-xs mb-1">
      <div class="ml-1">
        <Clock color="#5948a3" />
      </div>
      <div>
        <time datetime={ Date() } >
          Last updated { calculateTimeBetween(updated_at) }
        </time>
      </div>

       <div class="ml-1">
        <Tag color="#5948a3" />
      </div>
      <div class="text-black">{version}</div>

    </div>

  </a>
  
  