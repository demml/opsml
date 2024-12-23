<script lang="ts">
    import { onDestroy } from 'svelte';
    import Fa from 'svelte-fa'
    import { faClock} from '@fortawesome/free-solid-svg-icons'
    import { createEventDispatcher } from 'svelte';



    let isOpen: boolean = false;
    export let items: string[] = ['Option 1', 'Option 2', 'Option 3'];
    export let header: string;
    $: header = header;
  
    let dropdownRef;
    const dispatch = createEventDispatcher();


    function toggleDropdown() {
    isOpen = !isOpen;
    if (isOpen) {
      document.addEventListener('click', handleClickOutside);
    } else {
      document.removeEventListener('click', handleClickOutside);
    }
    }
  
    function selectItem(event, item) {
      event.preventDefault();
      header = item;
      isOpen = false;
      dispatch('change', { selected: item });
    }

    function handleClickOutside(event) {
    if (dropdownRef && !dropdownRef.contains(event.target)) {
      isOpen = false;
      document.removeEventListener('click', handleClickOutside);
    }
    }

    onDestroy(() => {
    document.removeEventListener('click', handleClickOutside);
    });



  </script>
  
  
    
  <div class="relative inline-block justify-center" bind:this={dropdownRef}>
    <button on:click={toggleDropdown} class="flex flex-row items-center justify-center border border-darkpurple bg-surface-100 hover:variant-soft-primary rounded w-28 h-8 px-2">
      <Fa class="h-4 mr-2" icon={faClock} color="#4b3978"/>
      <div class="text-darkpurple text-sm font-bold" >{header}</div>
      </button>
    {#if isOpen}
      <div class="absolute border border-darkpurple bg-surface-100 rounded shadow-lg text-sm w-24">
        {#each items as item}
          <button class="w-full block px-2 py-2 text-darkpurple font-bold text-sm hover:variant-soft-primary" on:click={(event) => selectItem(event, item)}>{item}</button>
        {/each}
      </div>
    {/if}
  </div>