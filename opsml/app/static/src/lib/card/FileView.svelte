
<script lang="ts">
  import {type FileView } from "$lib/scripts/types";


  export let name: string;
  export let modifiedAt: string;
  export let viewType: string;
  export let content: string | undefined;
</script>


<div class="flex flex-wrap">
  <div class="w-full md-full px-4 pt-8 md:px-20 text-sm">
    <div class="bg-gradient-to-b from-primary-50 to-white flex rounded-t-lg border border-gray px-3 py-2 min-w-96">
      <div class="inline-flex justify-between w-full items-center">
        <div class="text-primary-500 font-semibold">{name}</div>
        <div class="text-gray-500"> {modifiedAt}</div>
      </div>
    </div>

    {#if viewType === "code" && content}


      <div id="viewer" class="h-96"></div>
    {/if}

  </div>
</div>