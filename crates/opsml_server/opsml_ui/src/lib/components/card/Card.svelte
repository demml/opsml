<script lang="ts">

  import { calculateTimeBetween } from "$lib/utils";
  import { goto } from "$app/navigation";
  import {CircuitBoard } from 'lucide-svelte';

  let {
    name,
    repository,
    version,
    created_at,
    svgClass = "flex-none w-3 mr-0.5",
    hoverColor = "hover:text-secondary-600",
    hoverBorderColor = "hover:border-secondary-600",
    registry
  } = $props<{
    name: string;
    repository: string;
    version: string;
    created_at: string;
    svgClass?: string;
    hoverColor?: string;
    hoverBorderColor?: string;
    registry: string;
  }>();

  // function to navigate to the card page
  function navigateToCardPage() {
    // navigate to the card page
    goto(`/opsml/${registry}/card/home?name=${name}&repository=${repository}&version=${version}`);
  }


</script>

<button class="text-black rounded-base shadow border-2 border-border bg-primary-100 w-[450px] { hoverColor } hover:border-solid hover:border {hoverBorderColor}" onclick={navigateToCardPage}>
  <div class="flex items-center justify-start gap-2">
    <div>
      <CircuitBoard color="#00000" />
    </div>
    <div><h4 class="truncate font-bold">{repository}/{name}</h4></div>
  </div>
</button>

