
<script lang="ts">
import Highlight, { LineNumbers } from "svelte-highlight";
import json from "svelte-highlight/languages/json";
import intellijLight from "svelte-highlight/styles/intellij-light";

  /** @type {import('./$types').PageData} */
	export let data;

  let content = JSON.stringify(data.metadata, null, 2);

</script>

<svelte:head>
  {@html intellijLight }
</svelte:head>


<div class="flex items-center justify-center pt-8 text-sm">
  <div class="justify-center w-3/4">
    <div class="bg-surface-100 to-white flex rounded-t-lg border border-gray px-3 py-2 min-w-96">
      <div class="inline-flex justify-between w-full items-center">
        <div class="text-primary-500 font-semibold">Metadata for {data.metadata.model_name}</div>
      </div>
    </div>
    <div class="min-w-96 w-full border border-gray overflow-scroll">
      <Highlight language={json}  code={content} let:highlighted>
        <LineNumbers {highlighted} />
      </Highlight>
    </div>
  </div>
</div>
