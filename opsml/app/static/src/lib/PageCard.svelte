<script lang="ts">

  import { calculateTimeBetween } from "$lib/scripts/utils";
  export let name: string;
  export let repository: string;
  export let nbr_versions: number;
  export let updated_at: number;
  export let svgClass: string = "flex-none w-3 mr-0.5 fill-secondary-500 dark:fill-secondary-500";
  export let hoverColor: string = "hover:text-secondary-500";
  export let registry: string;

  
</script>
  
<a class= "block card max-w-96 border p-4 bg-gray-50 rounded-2xl { hoverColor } hover:border-solid hover:border hover:border-secondary-500 dark:bg-surface-700 dark:hover:bg-surface-600" href="/opsml/{registry}/home/card?name={name}&repository={repository}">
  <header class="flex items-center ml-0.5 mb-0.5" title="{repository}/{name}">
    <h4 class="truncate font-boing">{repository}/{name}</h4>
  </header>

  <div class="mr-1 ml-0.5 flex items-center overflow-hidden whitespace-nowrap text-sm leading-tight">
    <svg class="flex-none w-3 mr-1 {svgClass}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M 12 0 C 5.371094 0 0 5.371094 0 12 C 0 18.628906 5.371094 24 12 24 C 18.628906 24 24 18.628906 24 12 C 24 5.371094 18.628906 0 12 0 Z M 12 2 C 17.523438 2 22 6.476563 22 12 C 22 17.523438 17.523438 22 12 22 C 6.476563 22 2 17.523438 2 12 C 2 6.476563 6.476563 2 12 2 Z M 10.9375 3.875 L 10.5 12.0625 L 10.59375 12.9375 L 16.75 18.375 L 17.71875 17.375 L 12.625 11.96875 L 12.1875 3.875 Z"></path>
    </svg>
    <span class="truncate text-black dark:text-white">
      <time datetime={ Date() } >
        Last updated { calculateTimeBetween(updated_at / 1000) }
      </time>
    </span>
    <span class="px-1.5 text-black dark:text-white">- </span>
    <svg class="flex-none w-3 mr-0.5 {svgClass}" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
      <path d="M8 3a3 3 0 0 0-1 5.83v6.34a3.001 3.001 0 1 0 2 0V15a2 2 0 0 1 2-2h1a5.002 5.002 0 0 0 4.927-4.146A3.001 3.001 0 0 0 16 3a3 3 0 0 0-1.105 5.79A3.001 3.001 0 0 1 12 11h-1c-.729 0-1.412.195-2 .535V8.83A3.001 3.001 0 0 0 8 3Z"/>
    </svg>
    <div class="text-black dark:text-white"> {nbr_versions} versions</div>
  </div>
</a>
  