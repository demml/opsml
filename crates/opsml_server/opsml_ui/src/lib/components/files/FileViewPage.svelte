<script lang="ts">

  import { goto } from '$app/navigation';
  import FileViewer from '$lib/components/files/FileViewer.svelte';
  import type { RawFile } from "./types";
  
  
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
      registry: string;
      space: string;
      name: string;
      version: string;
    }>();
  
  
    export function goBack() {
      history.back();
    }
  
  
    function constructPath(index: number): string {
      const basePath = `/opsml/${registry}/card/${space}/${name}/${version}/files`;
      const dynamicPath = splitPath.slice(4, index + 1).join('/');
      return dynamicPath ? `${basePath}/${dynamicPath}` : `${basePath}`;
    }
  
    function gotoPath(index: number) {
      const path = constructPath(index);
      goto(path);
  
    }
  
  </script>
  
 

    <div class="w-full pt-4">
      <div class="rounded-lg border-2 border-black shadow overflow-x-auto bg-primary-500 py-2 mb-2 justify-center">
        <h1 class="ml-4 flex flex-row flex-wrap items-center">
          {#each splitPath as path, index}
            {#if index < 3}
              <div class="group flex flex-none items-center">
                <div class="font-semibold text-black hover:text-secondary-500">{path}</div>
                <div class="mx-0.5 text-gray-800">/</div>
              </div>
            {:else}
              {#if index == splitPath.length - 1}
                <div class="group flex flex-none items-center">
                  <div class="font-semibold text-black hover:text-secondary-500">{path}</div>
                </div>
              {:else}
                <div class="group flex flex-none items-center">
                  <button class="btn bg-white border-2 border-black shadow-small shadow-hover-small text-black rounded-lg mx-2" onclick={() => gotoPath(index)}>{path}</button>
                  <div class="mx-0.5 text-gray-800">/</div>
                </div>
              {/if}
            {/if}
  
          {/each}
        </h1>
  
      </div>
      <div class="rounded-lg border-2 border-black shadow overflow-x-auto bg-slate-100 overflow-y-auto">
        <FileViewer {file} />
      </div>
    </div>
 
  
  <style>
  
    :global(.markdown-body) {
      box-sizing: border-box;
      margin: 0 auto;
      width: 100%;
      font-size: medium;
    }
  
    :global(.markdown-body pre) {
      overflow-x: auto;
      white-space: nowrap;
    }
  
  </style>