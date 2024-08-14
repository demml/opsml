<script lang="ts">
    import FileSystem from "$lib/card/FileSystem.svelte";
    import Fa from 'svelte-fa'
    import { faFolder } from '@fortawesome/free-solid-svg-icons'
    import { type Files  } from "$lib/scripts/types";
    import { goto } from '$app/navigation';
  
  
    export let registry: string;
    export let name: string;
    export let repository: string;
    export let version: string;
    export let basePath: string;
    export let displayPath: string[];
    export let modifiedAt: string;
    export let subdir: string | null;
    export let fileInfo: Files;
    export let prevPath: string;
   
    function navigateToFolder(folderPath: string) {
      let subDir: string = folderPath.replace(`${basePath}/`, '');
      goto(`/opsml/${registry}/card/files?name=${name}&repository=${repository}&version=${version}&subdir=${subDir}`);
    }
  
    
  </script>
  
  
  
  <div class="flex items-center justify-center pt-2 text-sm">
  
    <div class="justify-center w-2/3">
  
      <div class="flex">
        {#each displayPath as path, index}
  
        {#if index !== displayPath.length - 1}
          <div class="font-bold mt-6 text-primary-500">{path}</div>
          <div class="font-bold mt-6 text-gray-500">&nbsp;/&nbsp;</div>
        {:else}
          <div class="font-bold mt-6 text-secondary-500">{path}</div>
        {/if}
        {/each}
      </div>
  
      <div class="bg-surface-100 to-white flex rounded-t-lg border border-gray px-3 py-2 min-w-96">
        <div class="inline-flex justify-between w-full items-center">
          <div class="text-primary-500 font-semibold">Files for {name}</div>
          <div class="text-primary-500"> {modifiedAt}</div>
        </div>
      </div>
  
      {#if subdir}
      <div class="w-full bg-white border border-gray-200 px-3 py-2 min-w-96">
        <div class="grid h-6 grid-cols-12 gap-x-3">
  
          <!-- svelte-ignore a11y-invalid-attribute -->
          <a class="flex flex-row col-span-8 md:col-span-4 items-center cursor-pointer hover:underline" href="#" role="button" on:click={() => navigateToFolder(prevPath)}>
            <Fa class="h-5 mr-2" icon={faFolder} color="#4b3978"/>
            <div class="flex truncate items-center text-black">..</div>
          </a>
        </div>
      </div>
      {/if}
  
      <FileSystem
        basePath={basePath}
        fileInfo={fileInfo}
        name={name}
        registry={registry}
        repository={repository}
        version={version}
      />
  
    </div>
  </div>
  