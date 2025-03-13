<script lang="ts">
  import { onMount } from "svelte";
  import logo from "$lib/images/opsml_word.webp";
  import { page } from "$app/state";
  import LogoutModal from "$lib/components/auth/LogoutModal.svelte";
  import { goto } from "$app/navigation";
  import { browser } from '$app/environment';
  import { Popover } from '@skeletonlabs/skeleton-svelte';
  import IconX from 'lucide-svelte/icons/x';
  import { KeySquare, Github } from 'lucide-svelte';
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
  <div class="mx-auto flex w-full items-center justify-between px-10 md:px-20">
    
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
      <div class="flex items-center justify-start gap-10">
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
              <a class="text-xl" href={path} class:active={page.url.pathname.includes(path)} data-sveltekit-preload-data="hover">
                {name}
              </a>
          {/each}
        </div>
      </div>
    </div>
    
    <div class="flex items-center gap-5 m1000:gap-5">
      <div class="flex items-center justify-end gap-5 m800:w-[unset] m400:gap-3">

        <a aria-label="Close" href="https://github.com/demml/opsml" class="m800:hidden flex gap-2 items-center justify-center rounded-base border-2 border-black shadow p-2 shadow-hover bg-surface-50">
          <Github color="#5948a3"/>
        </a>

        <button aria-label="Close" onclick={logInHandle} class="m800:hidden flex gap-2 items-center justify-center rounded-base border-2 border-black shadow p-2 shadow-hover bg-surface-50">
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
