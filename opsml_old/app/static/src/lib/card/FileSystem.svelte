<script lang="ts">

  import {type Files } from "$lib/scripts/types";
  import Fa from 'svelte-fa'
  import { faFile, faFolder } from '@fortawesome/free-solid-svg-icons'
  import { goto } from '$app/navigation';
  import { calculateTimeBetween } from "$lib/scripts/utils";  


  export let fileInfo: Files;
  export let basePath: string;
  export let name: string;
  export let registry: string;
  export let repository: string;
  export let version: string;


  function navigateToFolder(folderPath: string) {
    let subDir: string = folderPath.replace(`${basePath}/`, '');
    goto(`/opsml/${registry}/card/files?name=${name}&repository=${repository}&version=${version}&subdir=${subDir}`);
  }

  function viewFile(filePath: string) {
    goto(`/opsml/${registry}/card/files/view?name=${name}&repository=${repository}&version=${version}&path=${btoa(filePath)}`);
  }

</script>

{#each fileInfo.files as file}

  <div class="w-full bg-white border border-gray-200 px-3 py-2 min-w-96">
    <div class="grid h-6 grid-cols-12 gap-x-3">

  {#if file.type === 'file'}

    
    <!-- svelte-ignore a11y-invalid-attribute -->
    <a class="flex flex-row col-span-8 md:col-span-4 items-center cursor-pointer hover:underline" href="#" role="button" on:click={() => viewFile(file.uri)}>
        <Fa class="h-5 mr-2" icon={faFile} color="#4b3978"/>
        <div class="flex truncate items-center text-black">{file.name}</div>
    </a>

  {:else}
  
    <!-- svelte-ignore a11y-invalid-attribute -->
    <a class="flex flex-row col-span-8 md:col-span-4 items-center cursor-pointer hover:underline" href="#" role="button" on:click={() => navigateToFolder(file.uri)}>
      <Fa class="h-5 mr-2" icon={faFolder} color="#4b3978"/>
      <div class="flex truncate items-center text-black">{file.name}</div>
    </a>

  {/if}
    <div class="group col-span-4 flex items-center justify-self-end truncate text-right text-gray-500">{file.size} </div>
    <div class="col-span-4 hidden truncate items-center justify-self-end text-gray-400 md:block">{calculateTimeBetween(file.mtime)} </div>
    </div>
  </div>
{/each}
