<script lang="ts">
  import { goto } from '$app/navigation';
  import { getRegistryPath, type RegistryType } from '$lib/utils';
  import type { RawFile } from "./types";
  import FileViewer from './FileViewer.svelte';
  
  let { 
    file,
    splitPath,
    registry,
    space,
    name,
    version,
  } = $props<{
    file: RawFile;
    splitPath: string[];
    registry: RegistryType;
    space: string;
    name: string;
    version: string;
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

<!-- Main container with strict width constraints -->
<div class="pt-4 min-w-0 flex flex-col items-stretch max-h-full mx-auto max-w-6xl w-full px-4">
  <!-- Breadcrumb navigation -->
  <div class="w-full rounded-base border-2 border-black shadow-small bg-primary-100 py-2 mb-4 px-4">
    <div class="flex items-center flex-wrap gap-1">
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
              <button 
                class="btn bg-surface-50 border-2 border-black shadow-small shadow-hover-small text-primary-800 rounded-base mx-1 whitespace-nowrap text-sm font-medium font-mono" 
                onclick={() => gotoPath(index)}
              >
                {path}
              </button>
              <span class="mx-1 text-black/40 font-bold">/</span>
            </div>
          {/if}
        {/if}
      {/each}
    </div>
  </div>

  <div class="w-full rounded-base border-2 border-black shadow bg-surface-50 overflow-auto">
    <FileViewer {file} />
  </div>

</div>

