<script lang="ts">
  import {
  type Files,
} from "$lib/scripts/types";
  import { calculateTimeBetween } from "$lib/scripts/utils";  

  import Fa from 'svelte-fa'
  import { faFile, faFolderOpen } from '@fortawesome/free-solid-svg-icons'
  import { goto } from '$app/navigation';

  /** @type {import('./$types').PageData} */
	export let data;

  let tabSet: string = "files";

  let fileInfo: Files;
  $: fileInfo = data.files;

  let modifiedAt: string;
  $: modifiedAt = data.modifiedAt;

  let name: string;
  $: name = data.name;

  let basePath: string;
  $: basePath = data.basePath;

  function navigateToFolder(folderPath: string) {
    let subDir: sting = folderPath.replace(`${basePath}/`, '');
    goto(`/opsml/${registry}/card/files?name=${name}&repository=${repository}&version=${metadata.model_version}&subdir=${subDir}`);
  }


</script>

<div class="flex flex-wrap">
  <div class="w-full md-full px-4 pt-8 md:px-20 text-sm">
    <div class="bg-gradient-to-b from-primary-50 to-white flex rounded-t-lg border border-gray px-3 py-2 min-w-96">
      <div class="inline-flex justify-between w-full items-center">
        <div class="text-primary-500 font-semibold">Files for {name}</div>
        <div class="text-gray-500"> {modifiedAt}</div>
      </div>
    </div>

    {#each fileInfo.files as file}
      
      <div class="bg-white border border-gray-200 px-3 py-2 min-w-96">
        <div class="grid h-6 grid-cols-12 gap-x-3">
          {#if file.type === 'file'}
            <div class="flex flex-row col-span-8 md:col-span-4 items-center">
              <Fa class="h-5 mr-2" icon={faFile} color="#4b3978"/>
              <div class="flex truncate items-center text-black">{file.name}</div>
            </div>

          {:else}
          <a on:click={() => navigateToFolder(file.uri)} class="cursor-pointer">
            <div class="flex flex-row col-span-8 md:col-span-4 items-center">
                <Fa class="h-5 mr-2" icon={faFolderOpen} color="#4b3978"/>
                <div class="flex truncate items-center text-black">{file.name}</div>
            
            </div>
          </a>

          {/if}
          <div class="group col-span-4 flex items-center justify-self-end truncate text-right text-gray-500">{file.size} </div>
          <div class="col-span-4 hidden truncate items-center justify-self-end  text-gray-400 md:block">{calculateTimeBetween(file.mtime)} </div>
        </div>
      </div>

      
    {/each}
  </div>
</div>
