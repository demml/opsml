<script lang="ts">

    import { calculateTimeBetween, getRegistryTypeLowerCase, RegistryType } from "$lib/utils";
    import { goto } from "$app/navigation";
    import {CircuitBoard, Clock, Tag } from 'lucide-svelte';
  
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
  
    // function to navigate to the card page
    function navigateToCardPage() {
      // navigate to the card page
      let registry_name = getRegistryTypeLowerCase(registry);
      goto(`/opsml/${registry_name}/card/home?space=${space}&name=${name}&version=${version}`);
    }
  
  
  </script>
  
  <button class="text-black rounded-lg shadow border-2 border-black {bgColor} max-w-96 h-[84px] lg:h-[90px] overflow-auto whitespace-nowrap hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none" onclick={navigateToCardPage}>
    <div class="flex items-center justify-start gap-2">
      <div class="ml-2">
        <CircuitBoard color="#5948a3" />
      </div>
      <div><h4 class="truncate font-bold">{space}/{name}</h4></div>
    </div>
 
    <div class="flex items-center justify-start gap-2 overflow-hidden whitespace-nowrap text-xs lg:text-sm mb-1">
      <div class="ml-2">
        <Clock color="#5948a3" />
      </div>
      <div>
        <time datetime={ Date() } >
          Last updated { calculateTimeBetween(updated_at) }
        </time>
      </div>
    </div>

    <div class="flex items-center justify-start gap-2 overflow-hidden whitespace-nowrap text-xs lg:text-sm">
      <div class="ml-2">
        <Tag color="#5948a3" />
      </div>
      <div class="text-black">{version}</div>
    </div>
  </button>
  
  