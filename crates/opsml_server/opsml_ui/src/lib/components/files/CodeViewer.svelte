<script lang="ts">
  import { useLargeFileManager } from "./fileSizeManager.svelte";
  import { useVirtualScrolling } from './scrollManager.svelte';
  import { formatJson } from './utils';
  import "$lib/styles/hljs.css";
  import CodeBlock from "../codeblock/CodeBlock.svelte";


  interface Props {
    content: string;
    language: any;
    requiresProcessing?: boolean;
  }

  let { content, language, requiresProcessing = false }: Props = $props();
  

  const processedContent = $derived(
    requiresProcessing ? formatJson(content) : content
  );
  
  const fileManager = $derived(useLargeFileManager(processedContent));
  const virtualScroll = $derived(useVirtualScrolling(processedContent));

  let containerRef: HTMLElement | undefined = $state();
</script>


{#if fileManager.isLargeFile && !fileManager.showFullContent}
  <!-- Large File Preview Mode -->
  <div class="p-4 bg-yellow-50 border border-yellow-200 rounded-lg mb-2">
    <p class="text-yellow-800 mb-2">
      This is a large file ({fileManager.fileSizeKB.toFixed(1)}KB). 
      Showing first 100 lines for performance.
    </p>
    <div class="flex gap-3 items-center">
      <button 
        class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2"
        onclick={() => fileManager.toggleFullContent()}
      >
        Show Full Content
      </button>
      {#if fileManager.needsVirtualScrolling}
        <span class="text-sm text-gray-600">
          (Virtual scrolling will be used for smooth performance)
        </span>
      {/if}
    </div>
  </div>
  
  <div class="rounded-lg overflow-auto">
    <CodeBlock
        code={fileManager.getPreviewContent()} 
        showLineNumbers={true}
        lang={language}
      />
  </div>

{:else if fileManager.needsVirtualScrolling && fileManager.showFullContent}
  <div 
    bind:this={containerRef}
    class="h-[32rem] overflow-auto border rounded-lg"
    onscroll={virtualScroll.handleScroll}
    bind:clientHeight={virtualScroll.containerHeight}
  >
    <div style="height: {virtualScroll.totalHeight}px; position: relative;">
      <div 
        style="position: absolute; top: {virtualScroll.topOffset}px; width: 100%;" 
        class="rounded-lg overflow-hidden"
      >
        <CodeBlock
          code={processedContent} 
          showLineNumbers={true}
          lang={language}
        />
      </div>
    </div>
  </div>
  
{:else}
  {#if fileManager.showFullContent && fileManager.isLargeFile}
    <div class="p-2 bg-green-50 border border-green-200 rounded-lg mb-2">
      <div class="flex justify-between items-center">
        <p class="text-green-800 text-sm">Showing full content</p>
        <button 
          class="btn bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600"
          onclick={() => fileManager.toggleFullContent()}
        >
          Back to Preview
        </button>
      </div>
    </div>
  {/if}

  <CodeBlock
    code={processedContent} 
    showLineNumbers={true}
    lang={language}
  />
{/if}