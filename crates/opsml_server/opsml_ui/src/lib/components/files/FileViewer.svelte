<script lang="ts">
  import Highlight, { LineNumbers } from "svelte-highlight";
  import json from "svelte-highlight/languages/json";
  import python from "svelte-highlight/languages/python";
  import yaml from "svelte-highlight/languages/yaml";
  import sql from "svelte-highlight/languages/sql";
  import type { RawFile } from "./types";
  import { formatJson } from "./utils";
  import { convertMarkdown } from '$lib/components/readme/util';
  import { onMount } from 'svelte';


  let { 
    file,
  } = $props<{
    file: RawFile;
  }>();


  let convertedMarkdown: string = $state('')

  function isImage(mimeType: string): boolean {
    return mimeType.startsWith('image/');
  }

  onMount(async () => {
    if (file.suffix === 'md') {
      convertedMarkdown = await convertMarkdown(file.content);
    }
  });
  

</script>



<div class="w-full text-sm">
  {#if isImage(file.mime_type)}
    <div class="flex justify-center p-4">
      <img 
        src={`data:${file.mime_type};base64,${file.content}`} 
        alt="File preview"
        class="max-w-full h-auto rounded-lg shadow-lg"
      />
    </div>
  {:else if file.suffix === 'md'}
    <div class="markdown-body rounded-base px-4 pb-4 md:px-11 md:pb-11">
      {@html convertedMarkdown}
    </div>

  {:else if file.suffix === 'json' || file.suffix === 'jsonl' }
 
    <Highlight language={json}  code={formatJson(file.content)} let:highlighted>
        <LineNumbers {highlighted} />
    </Highlight>


  {:else if file.suffix === 'yaml' || file.suffix === 'yml'}

    <Highlight language={yaml} code={file.content} let:highlighted>
        <LineNumbers {highlighted} />
    </Highlight>
 

  {:else if file.suffix === 'py'}
    <Highlight language={python} code={file.content} let:highlighted>
        <LineNumbers {highlighted} />
    </Highlight>

  {:else if file.suffix === 'sql'}
    <Highlight language={sql} code={file.content} let:highlighted>
        <LineNumbers {highlighted} />
    </Highlight>

  {:else}
    <div class="markdown-body rounded-base px-4 pb-4 md:px-11 md:pb-11 w-full text-sm">
      {@html file.content}
    </div>
  {/if}
</div>
