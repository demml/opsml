
<script lang="ts">
  import {type FileView } from "$lib/scripts/types";


  import Highlight, { LineNumbers } from "svelte-highlight";
  import json from "svelte-highlight/languages/json";
  import python from "svelte-highlight/languages/python";
  import yaml from "svelte-highlight/languages/yaml";
  import a11yLight from "svelte-highlight/styles/a11y-light";
  import { marked } from 'marked';


  export let name: string;
  export let modifiedAt: string;
  export let viewType: string;
  export let content: string = "";
  export let suffix: string;

  
</script>

<svelte:head>
  {@html a11yLight}
</svelte:head>

<div class="flex flex-wrap">
  <div class="w-full md-full px-4 pt-8 md:px-20 text-sm">
    <div class="bg-gradient-to-b from-primary-50 to-white flex rounded-t-lg border border-gray px-3 py-2 min-w-96">
      <div class="inline-flex justify-between w-full items-center">
        <div class="text-primary-500 font-semibold">{name}</div>
        <div class="text-gray-500"> {modifiedAt}</div>
      </div>
    </div>

    {#if viewType === "code" && content && suffix}

    <div class="min-w-96 overflow-scroll">

      {#if suffix === "json"}

        <Highlight language={json}  code={content} let:highlighted>
          <LineNumbers {highlighted} />
        </Highlight>
      
      {:else if suffix === "py"}
        
          <Highlight language={python}  code={content} let:highlighted>
            <LineNumbers {highlighted} />
          </Highlight>
  
    
      {:else if suffix === "yaml" || suffix === "yml"}
          
            <Highlight language={yaml}  code={content} let:highlighted>
              <LineNumbers {highlighted} />
            </Highlight>

      {:else if suffix === "md"}



      {/if}

   
    

    </div>



    {/if}

  </div>
</div>