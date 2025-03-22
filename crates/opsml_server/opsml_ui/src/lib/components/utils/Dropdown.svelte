<script lang="ts">
 
 let { 
    selectedValue = $bindable(), 
    values = $bindable()
  } = $props<{
    selectedValue: String;
    values: String[];
  }>();


  let isOpen = $state(false);

  function toggleDropdown() {
      isOpen = !isOpen;
  }

  function selectValue(value: string) {
      selectedValue = value;
      isOpen = false;
  }

  // Close dropdown when clicking outside
  function handleClickOutside(event: MouseEvent) {
      const target = event.target as HTMLElement;
      if (!target.closest('.dropdown')) {
          isOpen = false;
      }
  }

</script>


<svelte:window on:click={handleClickOutside}/>

<div class="dropdown relative w-48">
    <button 
        type="button"
        onclick={toggleDropdown}
        class="w-full px-4 py-2 bg-primary-500 text-black border-black border-2 rounded-lg flex justify-between items-center"
    >
        <span>{selectedValue}</span>
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-down h-4 w-4" aria-hidden="true">
          <path d="m6 9 6 6 6-6"></path>
        </svg>
    </button>

    {#if isOpen}
      <div class="absolute top-full left-0 w-full mt-1 bg-primary-500 border-black border-2 rounded-lg overflow-hidden z-50 px-2 py-1">
        {#each values as value}
          <button
              class="w-full py-2 px-4 text-left border-2 border-transparent hover:border-black rounded-lg transition-colors text-black"
              onclick={() => selectValue(value)}
          >
              {value}
          </button>
        {/each}
      </div>
    {/if}
</div>