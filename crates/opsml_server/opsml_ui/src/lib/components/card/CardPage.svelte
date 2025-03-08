<script lang="ts">

    import { calculateTimeBetween } from "$lib/utils";
    import { goto } from "$app/navigation";
    import {CircuitBoard, Clock, Tag } from 'lucide-svelte';
  
    let {
      name,
      repository,
      version,
      registry,
      updated_at,
      nbr_versions,
      bgColor
    } = $props<{
      name: string;
      repository: string;
      version: string;
      registry: string;
      updated_at: string;
      nbr_versions: number;
      bgColor: string;
    }>();
  
    // function to navigate to the card page
    function navigateToCardPage() {
      // navigate to the card page
      goto(`/opsml/${registry}/card/home?name=${name}&repository=${repository}&version=${version}`);
    }
  
  
  </script>
  
  <button class="text-black rounded-lg shadow border-2 border-black {bgColor} max-w-96 h-[84px] overflow-hidden whitespace-nowrap hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none" onclick={navigateToCardPage}>
    <div class="flex items-center justify-start gap-2 mb-1">
      <div class="ml-2">
        <CircuitBoard color="#5948a3" />
      </div>
      <div><h4 class="truncate font-bold">{repository}/{name}</h4></div>
    </div>
 
      <div class="flex items-center justify-start gap-2 overflow-hidden whitespace-nowrap text-xs">
        <div class="ml-2">
          <Clock color="#5948a3" />
        </div>
        <div>
          <time datetime={ Date() } >
            Last updated { calculateTimeBetween(updated_at) }
          </time>
        </div>
      </div>

      <div class="flex items-center justify-start gap-2 overflow-hidden whitespace-nowrap text-xs">
        <div class="ml-2">
          <Tag color="#5948a3" />
        </div>
        <div class="text-black">{nbr_versions} versions</div>
      </div>
  </button>
  
  