<script lang="ts">
  import { convertMarkdown } from '$lib/components/readme/util';
  import { onMount } from 'svelte';


  let { content } = $props<{ content: string}>();
  let convertedMarkdown: string = $state('');

  onMount(async () => {
    convertedMarkdown = await convertMarkdown(content);
  });
</script>

{#if convertedMarkdown}
  <div class="markdown-body px-4 py-4 md:px-11 md:py-11 w-full">
    {@html convertedMarkdown}
  </div>
{:else}
  <div class="flex items-center justify-center p-8">
    <div class="animate-pulse text-gray-500">Loading markdown...</div>
  </div>
{/if}



<style>
  :global(.markdown-body) {
    box-sizing: border-box;
    margin: 0 auto;
    width: 100%;
    max-width: 100%;
    font-size: medium;
    overflow-wrap: break-word;
    word-wrap: break-word;
  }

  :global(.markdown-body pre) {
    overflow-x: auto;
    white-space: pre;
    max-width: 100%;
  }

  :global(.markdown-body code) {
    overflow-wrap: break-word;
    word-break: break-all;
    max-width: 100%;
  }

  /* Force any content inside FileViewer to respect container bounds */
  :global(.markdown-body *) {
    max-width: 100%;
  }
</style>