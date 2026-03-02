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
  <div class="p-4 bg-warning-300 border-2 border-black rounded-base shadow-small mb-2">
    <p class="text-black font-medium mb-2">
      This is a large file ({fileManager.fileSizeKB.toFixed(1)}KB). 
      Showing first 100 lines for performance.
    </p>
    <div class="flex gap-3 items-center">
      <button 
        class="btn text-sm bg-primary-500 text-white border-2 border-black shadow-small shadow-click-small rounded-base font-bold"
        onclick={() => fileManager.toggleFullContent()}
      >
        Show Full Content
      </button>
      {#if fileManager.needsVirtualScrolling}
        <span class="text-sm text-black/60">
          (Virtual scrolling will be used for smooth performance)
        </span>
      {/if}
    </div>
  </div>
  
  <div class="rounded-base overflow-auto border border-black">
    <CodeBlock
        code={fileManager.getPreviewContent()} 
        showLineNumbers={true}
        lang={language}
      />
  </div>

{:else if fileManager.needsVirtualScrolling && fileManager.showFullContent}
  <div 
    bind:this={containerRef}
    class="h-[32rem] overflow-auto border border-black rounded-base"
    onscroll={virtualScroll.handleScroll}
    bind:clientHeight={virtualScroll.containerHeight}
  >
    <div style="height: {virtualScroll.totalHeight}px; position: relative;">
      <div 
        style="position: absolute; top: {virtualScroll.topOffset}px; width: 100%;" 
        class="rounded-base overflow-hidden"
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
    <div class="p-2 bg-secondary-300 border-2 border-black rounded-base shadow-small mb-2">
      <div class="flex justify-between items-center">
        <p class="text-black text-sm font-medium">Showing full content</p>
        <button 
          class="btn bg-surface-50 text-primary-800 border-2 border-black shadow-small shadow-click-small rounded-base text-sm font-bold"
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