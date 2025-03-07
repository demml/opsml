<script lang="ts">
  import { onMount } from "svelte";
  import logo from "$lib/images/opsml_word.webp";
  import { page } from "$app/state";
  import LogoutModal from "$lib/components/auth/LogoutModal.svelte";
  import { goto } from "$app/navigation";
  import { browser } from '$app/environment';
  import { Popover } from '@skeletonlabs/skeleton-svelte';
  import IconX from 'lucide-svelte/icons/x';
  import { KeySquare } from 'lucide-svelte';
  import { RoutePaths } from "../api/routes";



  let popupState = $state(false);
  let popupMessage = $state('');
  let loaded = $state(false);


  let isSidebarOpen = $state(false);

  function toggleSidebar() {
    isSidebarOpen = !isSidebarOpen;
  }

  function handleLinkClick(path: string) {
    isSidebarOpen = false;
    goto(path);
  }


  function popoverClose() {
    popupState = false;
  }

  
  function logInHandle() {
    const currentPage = page.url.pathname;
    goto('/opsml/auth/login?url=' + currentPage);
  }

  
  function navigateToPath(name: string) {
    let path = `/opsml/${name}`;
    goto(path);
  }

  let imageLoaded = $state(false);

  const names = ["Models", "Data", "Prompts", "Experiments"];


  onMount(() => {
    const img = new Image();
    img.src = logo;
    img.onload = () => {
      imageLoaded = true;
    };
  });

</script>

<nav class="fixed left-0 top-0 z-20 mx-auto flex h-[75px] w-full items-center border-b-4 border-border bg-primary-700 border-b-2 border-black px-5 m500:h-16">
  <div class="mx-auto flex w-[1300px] max-w-full items-center justify-between">

    <div class="w-[236px] md:hidden" aria-label="hamburger">
      <button 
        type="button" 
        onclick={toggleSidebar}
        aria-label="Toggle menu" 
        aria-expanded={isSidebarOpen} 
        class="m800:hidden flex gap-2 items-center justify-center rounded-base border-2 border-border shadow p-2 transition-all hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none bg-surface-50"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-menu h-6 w-6 m500:h-4 m500:w-4">
          <line x1="4" x2="20" y1="12" y2="12"></line>
          <line x1="4" x2="20" y1="6" y2="6"></line>
          <line x1="4" x2="20" y1="18" y2="18"></line>
        </svg>
      </button>
    </div>

    <div class="hidden md:block">
      <div class="flex items-center gap-10">
        <a href="/opsml/home" class="items-center">
          <div class="w-[120px] h-10">
            <img 
              src={logo} 
              class="h-10 w-[120px] object-contain"
              alt="Opsml Logo"
            />
          </div>
        </a>

        <div class="flex items-center gap-10 m1100:gap-8">
          {#each names as name}
            {@const path = '/opsml/' + name.replace(/s$/, '').toLowerCase()}
              <a class="text-xl" href={path} class:active={page.url.pathname.includes(path)}>
                {name}
              </a>
          {/each}
        </div>
      </div>
    </div>
    
    <div class="flex items-center gap-5 m1000:gap-5">
      <div class="flex items-center justify-end gap-5 m800:w-[unset] m400:gap-3">
        <a target="_blank" aria-label="Close" href="/" class="m800:hidden flex gap-2 items-center justify-center rounded-base border-2 border-black shadow p-2 transition-all hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none bg-surface-50">
          <svg class="h-6 w-6 m500:h-4 m500:w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 496 512">
            <path class="fill-text dark:fill-darkText" d="M165.9 397.4c0 2-2.3 3.6-5.2 3.6-3.3 .3-5.6-1.3-5.6-3.6 0-2 2.3-3.6 5.2-3.6 3-.3 5.6 1.3 5.6 3.6zm-31.1-4.5c-.7 2 1.3 4.3 4.3 4.9 2.6 1 5.6 0 6.2-2s-1.3-4.3-4.3-5.2c-2.6-.7-5.5 .3-6.2 2.3zm44.2-1.7c-2.9 .7-4.9 2.6-4.6 4.9 .3 2 2.9 3.3 5.9 2.6 2.9-.7 4.9-2.6 4.6-4.6-.3-1.9-3-3.2-5.9-2.9zM244.8 8C106.1 8 0 113.3 0 252c0 110.9 69.8 205.8 169.5 239.2 12.8 2.3 17.3-5.6 17.3-12.1 0-6.2-.3-40.4-.3-61.4 0 0-70 15-84.7-29.8 0 0-11.4-29.1-27.8-36.6 0 0-22.9-15.7 1.6-15.4 0 0 24.9 2 38.6 25.8 21.9 38.6 58.6 27.5 72.9 20.9 2.3-16 8.8-27.1 16-33.7-55.9-6.2-112.3-14.3-112.3-110.5 0-27.5 7.6-41.3 23.6-58.9-2.6-6.5-11.1-33.3 2.6-67.9 20.9-6.5 69 27 69 27 20-5.6 41.5-8.5 62.8-8.5s42.8 2.9 62.8 8.5c0 0 48.1-33.6 69-27 13.7 34.7 5.2 61.4 2.6 67.9 16 17.7 25.8 31.5 25.8 58.9 0 96.5-58.9 104.2-114.8 110.5 9.2 7.9 17 22.9 17 46.4 0 33.7-.3 75.4-.3 83.6 0 6.5 4.6 14.4 17.3 12.1C428.2 457.8 496 362.9 496 252 496 113.3 383.5 8 244.8 8zM97.2 352.9c-1.3 1-1 3.3 .7 5.2 1.6 1.6 3.9 2.3 5.2 1 1.3-1 1-3.3-.7-5.2-1.6-1.6-3.9-2.3-5.2-1zm-10.8-8.1c-.7 1.3 .3 2.9 2.3 3.9 1.6 1 3.6 .7 4.3-.7 .7-1.3-.3-2.9-2.3-3.9-2-.6-3.6-.3-4.3 .7zm32.4 35.6c-1.6 1.3-1 4.3 1.3 6.2 2.3 2.3 5.2 2.6 6.5 1 1.3-1.3 .7-4.3-1.3-6.2-2.2-2.3-5.2-2.6-6.5-1zm-11.4-14.7c-1.6 1-1.6 3.6 0 5.9 1.6 2.3 4.3 3.3 5.6 2.3 1.6-1.3 1.6-3.9 0-6.2-1.4-2.3-4-3.3-5.6-2z">
            </path>
          </svg>
        </a>

        <button aria-label="Close" onclick={logInHandle} class="m800:hidden flex gap-2 items-center justify-center rounded-base border-2 border-black shadow p-2 transition-all hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none bg-surface-50">
          <KeySquare color="#5948a3"/>
        </button>
      </div>


    </div>

   

  </div>  
</nav>


<!-- Add this sidebar component after your nav element -->
{#if isSidebarOpen}
  <div 
    class="fixed inset-0 z-30 md:hidden pointer-events-none"
    role="dialog"
    tabindex="-1"
    aria-modal="true"
    aria-label="Navigation menu"
    onclick={toggleSidebar}
    onkeydown={e => {
      if (e.key === 'Escape' || e.key === 'Enter') {
        toggleSidebar();
      }
    }}
  >
    <div 
      class="fixed left-0 top-0 h-full w-64 bg-primary-700 shadow-lg z-40 pointer-events-auto"
      role="menu"
      tabindex="0"
      onclick={e => e.stopPropagation()}
      onkeydown={e => e.stopPropagation()}
    >
      <!-- Sidebar header -->
      <div class="flex items-center justify-between p-4  border-b-2 border-border">
        <button 
          type="button"
          class="items-center" 
          onclick={() => {
            isSidebarOpen = false;
            goto('/opsml/home');
          }}
        >
          <div class="w-[120px] h-10">
            <img 
              src={logo} 
              class="h-10 w-[120px] object-contain"
              alt="Opsml Logo"
            />
          </div>
        </button>
        <button 
          type="button"
          onclick={toggleSidebar}
          class="p-2"
          aria-label="Close menu"
        >
          <IconX class="h-6 w-6 hover:text-secondary-500 transition-colors duration-200" />
        </button>
      </div>

      <!-- Sidebar links -->
      <div class="flex flex-col py-4" role="menubar">
        {#each names as name}
          {@const path = '/opsml/' + name.replace(/s$/, '').toLowerCase()}
          <button 
            type="button"
            role="menuitem"
            onclick={() => handleLinkClick(path)}
            class="px-6 py-3 text-xl text-left hover:bg-surface-50 transition-colors duration-200"
            class:active={page.url.pathname.includes(path)}
            aria-current={page.url.pathname.includes(path) ? 'page' : undefined}
          >
            {name}
          </button>
        {/each}
      </div>
    </div>
  </div>
{/if}




<style>


  nav a:focus {
    text-decoration: underline;
    text-decoration-color: rgb(26, 255, 163);
    text-underline-offset: .75em;
  }

  nav a:hover {
    text-decoration: underline;
    text-decoration-color: rgb(26, 255, 163);
    text-underline-offset: .75em;
  }

  nav a.active {
    text-decoration: underline;
    text-decoration-color: rgb(26, 255, 163);
    text-underline-offset: .75em;
    font-weight: 700;
  }

</style>
