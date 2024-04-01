<script lang="ts">
  import {
  type Files,
} from "$lib/scripts/types";
  import { calculateTimeBetween } from "$lib/scripts/utils";  

  /** @type {import('./$types').PageData} */
	export let data;

  let tabSet: string = "files";

  let fileInfo: Files;
  $: fileInfo = data.files;

  let modifiedAt: string;
  $: modifiedAt = data.modifiedAt;

  let name: string;
  $: name = data.name;


</script>

<div class="flex flex-wrap">
  <div class="w-full md-full px-4 pt-8 md:px-20">
    <div class="bg-gradient-to-b from-primary-50 to-white flex rounded-t-lg border border-gray px-3 py-2 min-w-96">
      <div class="inline-flex justify-between w-full items-center">
        <div class="text-primary-500 font-semibold">Files for {name}</div>
        <div class="text-gray-500"> {modifiedAt}</div>
      </div>
    </div>

    {#each fileInfo.files as file}
      {#if file.type === 'file'}
        <div class="bg-white border border-gray-200 px-3 py-2 min-w-96">
          <div class="grid h-10 grid-cols-12 gap-4">
            <div class="col-span-8 md:col-span-4 lg:col-span-3 text-black">{file.name}</div>
            <div class="text-gray-500">{file.size} </div>
            <div class="text-gray-500">{calculateTimeBetween(file.mtime/1000)} </div>
          </div>
        </div>
      {/if}
    {/each}
  </div>
</div>
