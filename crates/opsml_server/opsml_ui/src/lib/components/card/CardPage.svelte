<script lang="ts">

    import { calculateTimeBetween, RegistryType } from "$lib/utils";
    import { goto } from "$app/navigation";
    import {CircuitBoard, Clock, Tag } from 'lucide-svelte';
  import { resolveCardPath, resolveCardPathFromArgs } from "./utils";
  
    let {
      name,
      space,
      version,
      registry,
      updated_at,
      nbr_versions,
      bgColor
    } = $props<{
      name: string;
      space: string;
      version: string;
      registry: RegistryType;
      updated_at: string;
      nbr_versions: number;
      bgColor: string;
    }>();
  
    // function to navigate to the card page
    function navigateToCardPage() {
      let path = resolveCardPathFromArgs(registry.toLowerCase(), space, name, version);
      goto(path);
    }
  
  
  </script>
  
  <button class="w-full mx-1 max-w-96 h-auto p-2 text-black rounded-lg shadow border-2 border-black {bgColor} hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none overflow-scroll" onclick={navigateToCardPage}>
    <div class="flex items-center justify-start gap-2 text-smd">
      <div class="ml-1">
        <CircuitBoard color="#5948a3" />
      </div>
      <div><h4 class="truncate font-bold text-smd mr-2">{space}/{name}</h4></div>
    </div>
 
    <div class="flex items-center justify-start gap-2 overflow-scroll whitespace-nowrap text-xs mb-1">
      
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
      <div class="text-black">{nbr_versions} versions</div>

    </div>

   
  </button>
  
  