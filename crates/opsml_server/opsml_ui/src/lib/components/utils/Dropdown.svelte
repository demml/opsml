<script lang="ts">
 
 let { 
    selectedValue = $bindable(), 
    values = $bindable(),
    width = 'w-[9rem]',
    py = 'py-2',
  } = $props<{
    selectedValue: string;
    values: string[];
    width: string;
    py: string;

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

<div class="dropdown relative {width}">
    <button 
        type="button"
        onclick={toggleDropdown}
        class="w-full text-sm px-2 {py} bg-primary-500 text-black border-black border-2 rounded-lg flex justify-between items-center overflow-x-auto"
    >
        <span>{selectedValue}</span>
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-down h-4 w-4" aria-hidden="true">
          <path d="m6 9 6 6 6-6"></path>
        </svg>
    </button>

    {#if isOpen}
      <div class="absolute top-full left-0 w-full mt-1 bg-primary-500 border-black border-2 rounded-lg z-50">
        <div class="max-h-72 overflow-y-auto overflow-x-auto px-1 py-1 custom-scrollbar">
        {#each values as value}
          <button
              class="min-w-full inline-flex text-sm {py} px-2 text-left border-2 border-transparent hover:border-black rounded-lg transition-colors text-black whitespace-nowrap"
              onclick={() => selectValue(value)}
          >
              {value}
          </button>
        {/each}
        </div>
      </div>
    {/if}
</div>


<style>
  /* Webkit browsers (Chrome, Safari) */
  .custom-scrollbar::-webkit-scrollbar {
    width: 4px;
  }

  .custom-scrollbar::-webkit-scrollbar-track {
    background: #e5e7eb;
    border-radius: 2px;
  }

  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: #ffffff;
    border-radius: 2px;
  }

  /* Firefox */
  .custom-scrollbar {
    scrollbar-width: thin;
    scrollbar-color: #ffffff #e5e7eb;
  }
</style>