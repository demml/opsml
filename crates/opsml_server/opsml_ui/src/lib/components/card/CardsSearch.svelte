
<script lang="ts">
  import { onMount } from "svelte";


  let { availableSpaces } = $props<{
    availableSpaces: string[];
  }>();
 
  let searchQuery = $state('');
  let filteredSpaces = $state<string[]>([]);
  let searchTerm = $state<string>('');

  onMount(() => {
    filteredSpaces = availableSpaces;
  });

  const searchSpaces = () => {	
		return filteredSpaces = availableSpaces.filter((item: string) => {
			let itemName = item.toLowerCase();
			return itemName.includes(searchTerm!.toLowerCase())
		})
	}

</script>



<div class="mx-auto w-11/12 min-h-screen pt-20 pb-10 m500:pt-14 lg:pt-[100px] flex justify-center">
  <div class="grid grid-cols-1 md:grid-cols-6 gap-4 w-full">
    <!-- Left column -->
    <div class="col-span-1 md:col-span-2 bg-secondary-200 p-4 flex flex-col">
      <!-- Top Section -->
      <div class="mb-4">
        <input
          type="text"
          bind:value={searchQuery}
          placeholder="Search..."
          class="w-full p-2 border border-gray-300 rounded"
          oninput={searchSpaces}
        />
      </div>

      <!-- Bottom Section -->
      <div class="space-y-2 flex flex-wrap pt-4 gap-1">
        <!-- Add your tags or other content here -->
        {#if searchTerm && filteredSpaces.length == 0}
          <p>No repositories found</p>
        {:else if filteredSpaces.length > 0}
          {#each filteredSpaces as space}
          <button class="chip hover:bg-primary-300 border border-1 border-gray-200 shadow-sm">{space}</button>
          {/each}
        {/if}
      </div>
    </div>

    <!-- Right column -->
    <div class="col-span-1 md:col-span-4 gap-4 bg-primary-200 p-4 flex flex-col">
      <!-- Add your items here -->
    </div>
  </div>
</div>