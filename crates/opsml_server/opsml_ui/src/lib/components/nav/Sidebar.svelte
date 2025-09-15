<script lang="ts">
  import { onMount } from "svelte";
  import { page } from "$app/state";
  import { goto } from "$app/navigation";
  import { 
    Home, 
    Database, 
    Brain, 
    MessageSquare, 
    FlaskConical, 
    Server,
    ChevronRight,
    Pin,
    PinOff
  } from 'lucide-svelte';

  interface Props {
    children: import('svelte').Snippet;
  }

  let { children }: Props = $props();

  let isExpanded = $state(false);
  let isPinned = $state(false);
  let hoverTimeout: number | null = null;

  const navItems = [
    { name: "Home", path: "/opsml/home", icon: Home },
    { name: "Spaces", path: "/opsml/space", icon: Database },
    { name: "Models", path: "/opsml/model", icon: Brain },
    { name: "Data", path: "/opsml/data", icon: Database },
    { name: "Prompts", path: "/opsml/prompt", icon: MessageSquare },
    { name: "Experiments", path: "/opsml/experiment", icon: FlaskConical },
    { name: "Services", path: "/opsml/service", icon: Server }
  ];

  function handleMouseEnter() {
    if (!isPinned) {
      if (hoverTimeout) clearTimeout(hoverTimeout);
      hoverTimeout = setTimeout(() => {
        isExpanded = true;
      }, 100);
    }
  }

  function handleMouseLeave() {
    if (!isPinned) {
      if (hoverTimeout) clearTimeout(hoverTimeout);
      hoverTimeout = setTimeout(() => {
        isExpanded = false;
      }, 300);
    }
  }

  function togglePin() {
    isPinned = !isPinned;
    if (isPinned) {
      isExpanded = true;
    } else {
      isExpanded = false;
    }
  }

  function handleNavClick(path: string) {
    goto(path);
  }

  function handleClickOutside(event: MouseEvent) {
    if (!isPinned) {
      const sidebar = document.querySelector('[data-sidebar]');
      if (sidebar && !sidebar.contains(event.target as Node)) {
        isExpanded = false;
      }
    }
  }

  onMount(() => {
    document.addEventListener('click', handleClickOutside);
    return () => {
      document.removeEventListener('click', handleClickOutside);
      if (hoverTimeout) clearTimeout(hoverTimeout);
    };
  });
</script>

<div class="flex h-full">
  <!-- Sidebar -->
  <aside 
    class="fixed start-0 top-[3.5rem] z-10 h-[calc(100dvh-3.5rem)] bg-white border-e-2 border-gray-200 shadow-lg transition-all duration-300 ease-in-out data-[expanded=true]:w-64 data-[expanded=false]:w-16"
    data-sidebar
    data-expanded={isExpanded}
    onmouseenter={handleMouseEnter}
    onmouseleave={handleMouseLeave}
  >
    <!-- Navigation Items -->
    <nav class="flex flex-col p-2 space-y-1">
      {#each navItems as item}
        {@const isActive = page.url.pathname === item.path || (item.path !== '/opsml/home' && page.url.pathname.includes(item.path))}
        <button
          type="button"
          onclick={() => handleNavClick(item.path)}
          class="flex items-center w-full p-3 rounded-lg transition-all duration-200 group relative {isActive 
            ? 'bg-purple-50 text-purple-700 border border-purple-200' 
            : 'text-gray-600 hover:bg-gray-50 hover:text-purple-600'}"
          aria-label={item.name}
          title={!isExpanded ? item.name : ''}
        >
          <div class="shrink-0 w-6 h-6 flex items-center justify-center">
            <svelte:component 
              this={item.icon} 
              size={20} 
              class="transition-colors duration-200 {isActive ? 'text-purple-700' : 'text-current'}"
            />
          </div>
          
          <span class="ms-3 text-sm font-medium whitespace-nowrap transition-opacity duration-300 {isExpanded ? 'opacity-100' : 'opacity-0'}">
            {item.name}
          </span>
          
          <!-- Active indicator -->
          {#if isActive}
            <div class="absolute start-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-purple-700 rounded-e-full"></div>
          {/if}
        </button>
      {/each}
    </nav>

    <!-- Pin/Unpin Button -->
    <div class="absolute bottom-4 start-2 end-2">
      <button
        type="button"
        onclick={togglePin}
        class="flex items-center w-full p-3 rounded-lg transition-all duration-200 text-gray-600 hover:bg-gray-50 hover:text-purple-600"
        aria-label={isPinned ? 'Unpin sidebar' : 'Pin sidebar'}
        title={!isExpanded ? (isPinned ? 'Unpin sidebar' : 'Pin sidebar') : ''}
      >
        <div class="shrink-0 w-6 h-6 flex items-center justify-center">
          {#if isPinned}
            <PinOff size={20} class="text-current" />
          {:else}
            <Pin size={20} class="text-current" />
          {/if}
        </div>
        
        <span class="ms-3 text-sm font-medium whitespace-nowrap transition-opacity duration-300 {isExpanded ? 'opacity-100' : 'opacity-0'}">
          {isPinned ? 'Unpin' : 'Pin sidebar'}
        </span>
        
        {#if isExpanded}
          <div class="ms-auto">
            <ChevronRight size={16} class="text-gray-400 transition-transform duration-200 {isExpanded ? 'rotate-180' : ''}" />
          </div>
        {/if}
      </button>
    </div>
  </aside>

  <!-- Main content area -->
  <main class="flex-1 transition-all duration-300 {isExpanded ? 'ms-64' : 'ms-16'}">
    {@render children()}
  </main>
</div>

<style>
  /* Ensure smooth transitions */
  aside {
    will-change: width;
  }
  
  /* Custom scrollbar for the sidebar */
  aside::-webkit-scrollbar {
    width: 4px;
  }
  
  aside::-webkit-scrollbar-track {
    background: transparent;
  }
  
  aside::-webkit-scrollbar-thumb {
    background: rgb(156 163 175 / 0.3);
    border-radius: 2px;
  }
  
  aside::-webkit-scrollbar-thumb:hover {
    background: rgb(156 163 175 / 0.5);
  }
</style>