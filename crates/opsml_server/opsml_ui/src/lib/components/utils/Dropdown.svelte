<script lang="ts">
 
 let { 
    isDropDownOpen , 
    selectedValue = $bindable(), 
    values = $bindable()
  } = $props<{
    isDropDownOpen: Boolean;
    selectedValue: String;
    values: String[];
  }>();


function selectValue(value: string) {
    selectedValue = value;
    isDropDownOpen = false;
  }

function toggleDropdown() {
  isDropDownOpen = !isDropDownOpen;
}

function clickOutside(node: HTMLElement) {
  const handleClick = (event: MouseEvent) => {
    if (!node.contains(event.target as Node)) {
      isDropDownOpen = false;
    }
  };

  document.addEventListener('click', handleClick, true);

  return {
    destroy() {
      document.removeEventListener('click', handleClick, true);
    }
  };
}
</script>

<div class="relative" use:clickOutside>
  <button 
    class="btn flex flex-row gap-2 bg-primary-500 border-black border-2 rounded-lg w-48 justify-between items-center"
    onclick={toggleDropdown}
  >
    <span class="text-black">{selectedValue}</span>
    <svg class="w-4 h-4 ml-2" fill="none" stroke="black" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
    </svg>
  </button>
  
  {#if isDropDownOpen}
    <div class="absolute top-full left-0 mt-1 w-48 bg-primary-500 border-2 border-black rounded-lg shadow-lg z-10 p-2">
      {#each values as value}
        <button
          class="w-full text-left px-4 py-1 mb-1 last:mb-0 hover:outline hover:outline-2 hover:outline-black text-black hover:rounded-lg"
          onclick={() => selectValue(value)}
        >
          {value}
        </button>
      {/each}
    </div>
  {/if}
</div>