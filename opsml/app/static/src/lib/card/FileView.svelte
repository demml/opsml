
<script lang="ts">
  import {type FileView } from "$lib/scripts/types";


  import Highlight, { LineNumbers } from "svelte-highlight";
  import json from "svelte-highlight/languages/json";
  import github from "svelte-highlight/styles/github";


  export let name: string;
  export let modifiedAt: string;
  export let viewType: string;
  export let content: string | undefined;
  export let suffix: string | undefined;

  
</script>

<svelte:head>
  {@html github}
</svelte:head>

<div class="flex flex-wrap">
  <div class="w-full md-full px-4 pt-8 md:px-20 text-sm">
    <div class="bg-gradient-to-b from-primary-50 to-white flex rounded-t-lg border border-gray px-3 py-2 min-w-96">
      <div class="inline-flex justify-between w-full items-center">
        <div class="text-primary-500 font-semibold">{name}</div>
        <div class="text-gray-500"> {modifiedAt}</div>
      </div>
    </div>

    {#if viewType === "code" && content}

    <div class="min-w-96 overflow-scroll">
      
      <Highlight language={json}  code={content}/>

    </div>



    {/if}

  </div>
</div>