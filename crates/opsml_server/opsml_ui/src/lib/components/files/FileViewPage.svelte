<script lang="ts">
  import { goto } from '$app/navigation';
  import { getRegistryPath, type RegistryType } from '$lib/utils';
  import type { RawFile } from "./types";
  import FileViewer from './FileViewer.svelte';
  import { X } from 'lucide-svelte';

  let {
    file,
    splitPath,
    registry,
    space,
    name,
    version,
    disableNavigation = false,
    onClose,
  } = $props<{
    file: RawFile;
    splitPath: string[];
    registry: RegistryType;
    space: string;
    name: string;
    version: string;
    disableNavigation?: boolean;
    onClose?: () => void;
  }>();

  export function goBack() {
    history.back();
  }

  function constructPath(index: number): string {
    const basePath = `/opsml/${getRegistryPath(registry)}/card/${space}/${name}/${version}/files`;
    const dynamicPath = splitPath.slice(4, index + 1).join('/');
    return dynamicPath ? `${basePath}/${dynamicPath}` : `${basePath}`;
  }

  function gotoPath(index: number) {
    const path = constructPath(index);
    goto(path);
  }
</script>

<!-- Main container -->
<div class="min-w-0 w-full pt-2 pb-8">
  <!-- Breadcrumb — sticks to top of right panel's scroll container -->
  <div class="top-0 z-5 w-full rounded-base border-2 border-black shadow-small bg-primary-100 py-2 mb-4 px-4 flex items-center gap-2">
    <div class="flex items-center flex-wrap gap-1 flex-1 min-w-0">
      {#each splitPath as path, index}
        {#if index < 3}
          <div class="flex items-center">
            <span class="font-mono text-sm font-medium text-primary-800 whitespace-nowrap">{path}</span>
            <span class="mx-1 text-black/40 font-bold">/</span>
          </div>
        {:else}
          {#if index == splitPath.length - 1}
            <div class="flex items-center">
              <span class="font-mono text-sm font-bold text-black whitespace-nowrap">{path}</span>
            </div>
          {:else}
            <div class="flex items-center">
              {#if disableNavigation}
                <span class="font-mono text-sm font-medium text-primary-700 whitespace-nowrap mx-1">{path}</span>
              {:else}
                <button
                  class="btn bg-surface-50 border-2 border-black shadow-small shadow-hover-small text-primary-800 rounded-base mx-1 whitespace-nowrap text-sm font-medium font-mono"
                  onclick={() => gotoPath(index)}
                >
                  {path}
                </button>
              {/if}
              <span class="mx-1 text-black/40 font-bold">/</span>
            </div>
          {/if}
        {/if}
      {/each}
    </div>
    {#if onClose}
      <button
        class="btn text-sm bg-surface-50 text-primary-800 border-2 border-black shadow-small shadow-click-small rounded-base font-bold flex items-center gap-1 shrink-0 ml-auto"
        onclick={onClose}
      >
        <X class="w-4 h-4" /> Close
      </button>
    {/if}
  </div>

  <div class="w-full rounded-base border-2 border-black shadow bg-surface-50 overflow-x-auto">
    <FileViewer {file} />
  </div>

</div>

