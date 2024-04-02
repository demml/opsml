
<script lang="ts">
  import {type FileInfo } from "$lib/scripts/types";

  export let name: string;
  export let fileInfo : FileInfo;

</script>


<div class="flex flex-wrap">
  <div class="w-full md-full px-4 pt-8 md:px-20 text-sm">
    <div class="bg-gradient-to-b from-primary-50 to-white flex rounded-t-lg border border-gray px-3 py-2 min-w-96">
      <div class="inline-flex justify-between w-full items-center">
        <div class="text-primary-500 font-semibold">{name}</div>
        <div class="text-gray-500"> {modifiedAt}</div>
      </div>
    </div>

    {#if fileInfo.viewable}
      <!-- Add iframe for fileInfo uri -->
      <iframe
        src={fileInfo.uri}
        class="w-full h-96"
        frameborder="0"
        allowfullscreen
      ></iframe>
    {:else}
      <div class="bg-gradient-to-b from-secondary-50 to-white rounded-lg text-center items-center">
        <p class="mb-1">File is not viewable</p>
      </div>
    {/if}

  </div>
  </div>