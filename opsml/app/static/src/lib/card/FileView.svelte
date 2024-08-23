
<script lang="ts">
 

  import Highlight, { LineNumbers } from "svelte-highlight";
  import json from "svelte-highlight/languages/json";
  import python from "svelte-highlight/languages/python";
  import yaml from "svelte-highlight/languages/yaml";
  import sql from "svelte-highlight/languages/sql";
  import atomOneLight from "svelte-highlight/styles/atom-one-light";
  import Markdown from "$lib/card/Markdown.svelte";

  function formatJson(jsonString: string): string {
    console.log(jsonString);
    let newJson = JSON.stringify(JSON.parse(jsonString), null, 2);
    console.log(newJson);
    return newJson;
  }


  export let name: string;
  export let modifiedAt: string;
  export let viewType: string | undefined;
  export let content: string | undefined;
  export let suffix: string | undefined;
  export let uri: string | undefined;

  
</script>

<svelte:head>
  {@html atomOneLight}
</svelte:head>

<div class="flex items-center justify-center pt-8 text-sm">

  <div class="justify-center w-3/4">

    <div class="bg-surface-200 flex rounded-t-lg border border-gray px-3 py-2 min-w-96">
      <div class="inline-flex justify-between w-full items-center">
        <div class="text-primary-500 font-semibold">{name}</div>
        <div class="text-primary-500"> {modifiedAt}</div>
      </div>
    </div>

    <div class="min-w-96 w-full border border-gray overflow-scroll">

      {#if viewType === "code" && content && suffix}

        {#if suffix === "json" || suffix === "jsonl"}

          <Highlight language={json}  code={formatJson(content)} let:highlighted>
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

        {:else if suffix === "sql"}
      
          <Highlight language={sql}  code={content} let:highlighted>
            <LineNumbers {highlighted} />
          </Highlight>

        {:else if suffix === "md"}

          <Markdown source={content}/>

        {/if}
  

      {:else if viewType === "iframe" && uri}

        {#if suffix === "jpeg" || suffix === "jpg" || suffix === "png" || suffix === "gif" || suffix === "tiff"}

        <div class="flex justify-center items-center">
          <img src={uri} alt={name} class="center"/>
        </div>

        {/if}

      {:else}
        <div class="p-4 text-center text-gray-500">No content to display</div>
      {/if}
    </div>
  </div>
</div>