<script lang="ts">
  import { onMount } from "svelte";
  import { page } from "$app/state";
  import { goto } from "$app/navigation";
  import { 
    Home, 
    Database, 
    Brain, 
    Sparkles,
    NotebookTabs,
    FlaskConical, 
    Server,
    ChevronRight,
    Pin,
    PinOff,
    Activity
  } from 'lucide-svelte';

  interface NavSubItem {
    name: string;
    path: string;
  }

  interface NavItem {
    name: string;
    path: string;
    icon: any;
    subItems?: NavSubItem[];
  }

  interface Props {
    children: import('svelte').Snippet;
  }

  let { children }: Props = $props();

  let isExpanded = $state(false);
  let isPinned = $state(false);
  let hoverTimeout: ReturnType<typeof setTimeout> | null = null;
  let expandedItems = $state<Set<string>>(new Set());

  const navItems: NavItem[] = [
    { name: "Home", path: "/opsml/home", icon: Home },
    { name: "Spaces", path: "/opsml/space", icon: NotebookTabs },
    { name: "Models", path: "/opsml/model", icon: Brain },
    { name: "Data", path: "/opsml/data", icon: Database },
    { 
      name: "GenAI", 
      path: "/opsml/genai", 
      icon: Sparkles,
      subItems: [
        { name: "Prompts", path: "/opsml/genai/prompt" },
        { name: "Agents", path: "/opsml/genai/agent" },
        { name: "MCPs", path: "/opsml/genai/mcp" }
      ]
    },
    { name: "Experiments", path: "/opsml/experiment", icon: FlaskConical },
    { name: "Services", path: "/opsml/service", icon: Server },
    { name: "Observability", path: "/opsml/observability", icon: Activity }
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

  function toggleSubMenu(itemName: string) {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(itemName)) {
      newExpanded.delete(itemName);
    } else {
      newExpanded.add(itemName);
    }
    expandedItems = newExpanded;
  }

  function isItemActive(item: NavItem): boolean {
    if (page.url.pathname === item.path) return true;
    if (item.path !== '/opsml/home' && page.url.pathname.includes(item.path)) return true;
    if (item.subItems) {
      return item.subItems.some(subItem => page.url.pathname === subItem.path || page.url.pathname.includes(subItem.path));
    }
    return false;
  }

  function isSubItemActive(subItem: NavSubItem): boolean {
    return page.url.pathname === subItem.path || page.url.pathname.includes(subItem.path);
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

  <aside 
    class="fixed start-0 top-[3.5rem] z-30 h-[calc(100dvh-3.5rem)] bg-surface-100 border-e-2 border-black shadow-lg transition-all duration-300 ease-in-out data-[expanded=true]:w-64 data-[expanded=false]:w-16"
    data-sidebar
    data-expanded={isExpanded}
    onmouseenter={handleMouseEnter}
    onmouseleave={handleMouseLeave}
  >

    <nav class="flex flex-col p-2 space-y-1 overflow-y-scroll h-full">
      {#each navItems as item}
        {@const isActive = isItemActive(item)}
        {@const IconComponent = item.icon}
        {@const hasSubItems = item.subItems && item.subItems.length > 0}
        {@const isSubMenuExpanded = expandedItems.has(item.name)}
        
        <div>
          <button
            type="button"
            onclick={() => hasSubItems ? toggleSubMenu(item.name) : handleNavClick(item.path)}
            class="flex items-center w-full h-12 p-3 rounded-lg transition-all duration-200 group relative box-border pl-3
              border
              {isActive
                ? 'bg-primary-50 text-primary-800 border-primary-200'
                : 'text-black hover:bg-gray-50 hover:text-primary-700 border-transparent'}
            "
            aria-label={item.name}
            title={!isExpanded ? item.name : ''}
          >
            <div class="absolute left-0 top-1/2 -translate-y-1/2 h-8 w-1 {isActive ? 'bg-primary-700' : 'bg-transparent'} rounded-e-full"></div>
            <div class="shrink-0 w-6 h-6 flex items-center justify-center">
              <IconComponent 
                size={20} 
                class="transition-colors duration-200 {isActive ? 'text-primary-800' : 'text-current'}"
              />
            </div>
            <span class="ms-3 text-sm font-medium whitespace-nowrap transition-opacity duration-300 {isExpanded ? 'opacity-100' : 'opacity-0'}">
              {item.name}
            </span>
            {#if hasSubItems && isExpanded}
              <div class="ms-auto">
                <ChevronRight 
                  size={16} 
                  class="text-black transition-transform duration-200 {isSubMenuExpanded ? 'rotate-90' : ''}" 
                />
              </div>
            {/if}
          </button>

          {#if hasSubItems && isSubMenuExpanded && isExpanded}
            <div class="ms-6 mt-1 space-y-1">
              {#each item.subItems ?? [] as subItem}
                {@const isSubActive = isSubItemActive(subItem)}
                <button
                  type="button"
                  onclick={() => handleNavClick(subItem.path)}
                  class="flex items-center w-full py-2 px-3 rounded-md text-sm transition-all duration-200 {isSubActive
                    ? 'bg-primary-100 text-primary-700 font-medium'
                    : 'text-black hover:bg-gray-50 hover:text-primary-600'}"
                  aria-label={subItem.name}
                >
                  <div class="w-2 h-2 rounded-full me-3 {isSubActive ? 'bg-primary-600' : 'bg-gray-300'}"></div>
                  {subItem.name}
                </button>
              {/each}
            </div>
          {/if}
        </div>
      {/each}
    </nav>

    <div class="absolute bottom-0 start-0 end-0 p-2 bg-white border-t border-gray-100">
      <button
        type="button"
        onclick={togglePin}
        class="flex items-center w-full p-3 rounded-lg transition-all duration-200 text-gray-600 hover:bg-gray-50 hover:text-primary-700"
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

  <main class="flex-1 transition-all duration-300 {isExpanded ? 'ms-64' : 'ms-16'}">
    {@render children()}
  </main>
</div>

<style>
 
  aside {
    will-change: width;
  }
  
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