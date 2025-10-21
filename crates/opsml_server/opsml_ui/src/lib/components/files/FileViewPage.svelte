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
<div class="pt-4 min-w-0 flex flex-col items-stretch max-h-full mx-auto w-sm sm:w-xl md:w-3xl lg:w-5xl xl:w-6xl">
  <!-- Breadcrumb navigation -->
  <div class="w-full rounded-lg border-2 border-black shadow bg-primary-500 py-2 mb-4 px-4">
    <div class="flex items-center flex-wrap">
      {#each splitPath as path, index}
        {#if index < 3}
          <div class="flex items-center">
            <span class="font-semibold text-black hover:text-secondary-500 whitespace-nowrap">{path}</span>
            <span class="mx-0.5 text-gray-800">/</span>
          </div>
        {:else}
          {#if index == splitPath.length - 1}
            <div class="flex items-center">
              <span class="font-semibold text-black hover:text-secondary-500 whitespace-nowrap">{path}</span>
            </div>
          {:else}
            <div class="flex items-center">
              <button 
                class="btn bg-white border-2 border-black shadow-small shadow-hover-small text-black rounded-lg mx-2 whitespace-nowrap" 
                onclick={() => gotoPath(index)}
              >
                {path}
              </button>
              <span class="mx-0.5 text-gray-800">/</span>
            </div>
          {/if}
        {/if}
      {/each}
    </div>
  </div>

  <div class="w-full rounded-lg border-2 border-black shadow bg-white overflow-auto">
    <FileViewer {file} />
  </div>

</div>

