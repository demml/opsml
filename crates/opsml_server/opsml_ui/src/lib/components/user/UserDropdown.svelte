<script lang="ts">
  import { UserRound } from "lucide-svelte";


  let isOpen = $state(false);

  function toggleDropdown() {
      isOpen = !isOpen;
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

<div class="dropdown relative">
    <button 
        type="button"
        onclick={toggleDropdown}
        class="custom-scrollbar"
    >
        <UserRound color="#5948a3"/>
    </button>

    {#if isOpen}
      <div class="absolute top-full left-0 w-full mt-1 bg-primary-500 border-black border-2 rounded-lg z-50">
        <div class="max-h-72 overflow-y-auto px-2 py-1 custom-scrollbar">
        {#each values as value}
          <button
              class="w-full {py} px-4 text-left border-2 border-transparent hover:border-black rounded-lg transition-colors text-black"
              onclick={() => selectValue(value)}
          >
              {value}
          </button>
        {/each}
        </div>
      </div>
    {/if}

</div>


