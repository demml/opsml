<script lang="ts">

  import { calculateTimeBetween } from "$lib/utils";
  import { goto } from "$app/navigation";
  import {CircuitBoard, Clock, Tag } from 'lucide-svelte';

  let {
    name,
    repository,
    version,
    created_at,
    registry,
    cardColor,
    iconColor = "#000000"
  } = $props<{
    name: string;
    repository: string;
    version: string;
    created_at: string;
    registry: string;
    cardColor: string;
  }>();

  // function to navigate to the card page
  function navigateToCardPage() {
    // navigate to the card page
    goto(`/opsml/${registry}/card/home?name=${name}&repository=${repository}&version=${version}`);
  }


</script>

<button class="text-black rounded-base shadow border-2 border-border {cardColor} w-[400px] h-[75px] overflow-hidden whitespace-nowrap hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none" onclick={navigateToCardPage}>
  <div class="flex items-center justify-start gap-2 mb-1">
    <div class="ml-2">
      <CircuitBoard color={iconColor} />
    </div>
    <div><h4 class="truncate font-bold text-lg">{repository}/{name}</h4></div>
  </div>
  <div class="flex items-center justify-start gap-2 overflow-hidden whitespace-nowrap text-xs">
    <div class="flex items-center gap-1 ">
      <div class="ml-2">
        <Clock color={iconColor} />
      </div>
      <div>
        <time datetime={ Date() } >
          Updated { calculateTimeBetween(created_at) }
        </time>
      </div>
    </div>
    <div class="flex items-center gap-1 ">
      <div class="ml-2">
        <Tag color={iconColor} />
      </div>
      <div class="text-black">Version: {version}</div>
    </div>
  </div>
</button>

