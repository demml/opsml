<script lang="ts">
  
  import CardsSearch from "$lib/components/card/CardsSearch.svelte";
  import type { PageProps } from './$types';
  import { onMount } from "svelte";
  import type { SpacesResponse, SpaceStats } from "$lib/components/card/types";
  import { ArrowLeft, ArrowRight, Search, Settings } from 'lucide-svelte';

  let { data }: PageProps = $props();
  let spaces: SpacesResponse  = data.spaces;

  let currentPage = $state(1);
  let totalPages = $state(1);

  let searchQuery = $state('');
  let filteredSpaces = $state<SpaceStats[]>([]);
  let availableSpaces = spaces.spaces


  const searchSpaces = () => {	
    // filter based on item.space
    return filteredSpaces = availableSpaces.filter((item: SpaceStats) => {
      let itemName = item.space.toLowerCase();
      return itemName.includes(searchQuery!.toLowerCase())
    })
  }

  onMount(() => {
    // get first 30 spaces
    filteredSpaces = spaces.spaces.slice(0, 30);
    totalPages = Math.ceil(spaces.spaces.length / 30);
  });


  const changePage = async function (page: number) {
    // change page (slice based on page number)
    if (page < 1 || page > totalPages) return;

    const start = (page - 1) * 30;
    const end = start + 30;
    filteredSpaces = spaces.spaces.slice(start, end);

    currentPage = page;
  }


</script>

<div class="mx-auto w-9/12 pt-20 pt-[100px] flex justify-center px-4">

  <div class="gap-1 p-4 flex flex-col rounded-base border-primary-500 border-2 shadow-primary bg-surface-50 h-auto">
    <div class="flex flex-row items-center gap-2 pb-2">
      <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
        <Settings color="#40328b" />
      </div>
      <h2 class="font-bold text-primary-800 text-xl">Spaces</h2>
    </div>

  </div>

</div>