
<script lang="ts">
    import {type FileView } from "$lib/scripts/types";
  
  
    import Highlight, { LineNumbers } from "svelte-highlight";
    import sql from "svelte-highlight/languages/sql";
    import atomOneLight from "svelte-highlight/styles/atom-one-light";
    import Markdown from "$lib/card/Markdown.svelte";
    import { type DataCardMetadata } from "$lib/scripts/types";
    import { clipboard } from '@skeletonlabs/skeleton';
  
  
    /** @type {import('./$types').LayoutData} */
    export let data;
    
    let metadata: DataCardMetadata;
    $: metadata = data.metadata;

    let sqlLogic: Map<string, string>;
    $: sqlLogic = data.metadata.sql_logic;

  </script>
  
  <svelte:head>
    {@html atomOneLight}
  </svelte:head>
  
  <div class="flex flex-col items-center pt-8 text-sm">
    {#each Object.keys(sqlLogic) as key}
        <div class="justify-center w-3/4 pb-4">

          <div class="bg-gradient-to-b from-primary-50 to-white flex rounded-t-lg border border-gray px-3 py-2 min-w-96">
            <div class="inline-flex justify-between w-full items-center">
              <div class="text-primary-500 font-semibold">{key}</div>
              <button use:clipboard={sqlLogic[key]} class="btn btn-sm variant-filled">Copy</button>
            </div>
          </div>

          <div class="min-w-96 w-full border border-gray overflow-scroll">
            <Highlight language={sql}  code={sqlLogic[key]} let:highlighted>
              <LineNumbers {highlighted} />
            </Highlight>
          </div>

        </div>
      {/each}
  </div>

