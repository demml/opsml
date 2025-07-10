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
  let isLargeFile: boolean = $state(false)
  let showFullContent: boolean = $state(false)
  let useVirtualScrolling: boolean = $state(false)
  
  // Virtual scrolling state
  let containerRef: HTMLElement | undefined = $state()
  let visibleContent: string = $state('')
  let scrollTop: number = $state(0)
  let containerHeight: number = $state(600)
  
  const LARGE_FILE_THRESHOLD = 50000; // 50KB threshold
  const VIRTUAL_SCROLL_THRESHOLD = 200000; // 200KB threshold
  const PREVIEW_LINES = 100;
  const LINE_HEIGHT = 20;
  const BUFFER_LINES = 20;

  function isImage(mimeType: string): boolean {
    return mimeType.startsWith('image/');
  }

  function truncateContent(content: string, maxLines: number): string {
    const lines = content.split('\n');
    if (lines.length <= maxLines) return content;
    return lines.slice(0, maxLines).join('\n');
  }

  function updateVirtualContent(content: string) {
    if (!containerRef) return;
    
    const lines = content.split('\n');
    const totalLines = lines.length;
    
    const startLine = Math.max(0, Math.floor(scrollTop / LINE_HEIGHT) - BUFFER_LINES);
    const visibleLines = Math.ceil(containerHeight / LINE_HEIGHT) + (BUFFER_LINES * 2);
    const endLine = Math.min(totalLines, startLine + visibleLines);
    
    visibleContent = lines.slice(startLine, endLine).join('\n');
  }

  function handleScroll(e: Event) {
    if (!useVirtualScrolling) return;
    const target = e.target as HTMLElement;
    scrollTop = target.scrollTop;
    updateVirtualContent(getProcessedContent());
  }

  function getProcessedContent(): string {
    if (file.suffix === 'json' || file.suffix === 'jsonl') {
      return formatJson(file.content);
    }
    return file.content;
  }

  function getLanguage() {
    switch (file.suffix) {
      case 'json':
      case 'jsonl':
        return json;
      case 'yaml':
      case 'yml':
        return yaml;
      case 'py':
        return python;
      case 'sql':
        return sql;
      default:
        return json;
    }
  }

  onMount(async () => {
    if (file.suffix === 'md') {
      convertedMarkdown = await convertMarkdown(file.content);
    }
    
    // Determine file size and scrolling strategy
    const contentSize = file.content.length;
    isLargeFile = contentSize > LARGE_FILE_THRESHOLD;
    useVirtualScrolling = contentSize > VIRTUAL_SCROLL_THRESHOLD;
    
    if (useVirtualScrolling && showFullContent) {
      updateVirtualContent(getProcessedContent());
    }
  });

  // Update virtual content when showFullContent changes
  $effect(() => {
    if (useVirtualScrolling && showFullContent) {
      updateVirtualContent(getProcessedContent());
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
  {:else if ['json', 'jsonl', 'yaml', 'yml', 'py', 'sql'].includes(file.suffix)}
    {#if isLargeFile && !showFullContent}
      <!-- Preview Mode -->
      <div class="p-4 bg-yellow-50 border border-yellow-200 rounded-lg mb-2">
        <p class="text-yellow-800 mb-2">
          This is a large file ({(file.content.length / 1024).toFixed(1)}KB). 
          Showing first {PREVIEW_LINES} lines for performance.
        </p>
        <div class="flex gap-3">
          <button 
            class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2"
            onclick={() => showFullContent = true}
          >
            Show Full Content
          </button>
          {#if useVirtualScrolling}
            <span class="text-sm text-gray-600 flex items-center">
              (Virtual scrolling will be used for smooth performance)
            </span>
          {/if}
        </div>
      </div>
      <Highlight 
        language={getLanguage()} 
        code={truncateContent(getProcessedContent(), PREVIEW_LINES)} 
        let:highlighted
      >
        <LineNumbers {highlighted} />
      </Highlight>
    {:else if useVirtualScrolling && showFullContent}
      <!-- Virtual Scrolling Mode for very large files -->
      <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg mb-2">
        <div class="flex justify-between items-center">
          <p class="text-blue-800">
            Virtual scrolling enabled for performance ({(file.content.length / 1024).toFixed(1)}KB file)
          </p>
          <button 
            class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2"
            onclick={() => showFullContent = false}
          >
            Back to Preview
          </button>
        </div>
      </div>
      <div 
        bind:this={containerRef}
        class="h-[32rem] overflow-auto border rounded-lg"
        onscroll={handleScroll}
        bind:clientHeight={containerHeight}
      >
        <div style="height: {getProcessedContent().split('\n').length * LINE_HEIGHT}px; position: relative;">
          <div style="position: absolute; top: {Math.max(0, Math.floor(scrollTop / LINE_HEIGHT) - BUFFER_LINES) * LINE_HEIGHT}px; width: 100%;">
            <Highlight 
              language={getLanguage()} 
              code={visibleContent} 
              let:highlighted
            >
              <LineNumbers 
                {highlighted} 
                startingLineNumber={Math.max(1, Math.floor(scrollTop / LINE_HEIGHT) - BUFFER_LINES + 1)}
              />
            </Highlight>
          </div>
        </div>
      </div>
    {:else}
      <!-- Normal Mode -->
      {#if showFullContent && isLargeFile}
        <div class="p-2 bg-green-50 border border-green-200 rounded-lg mb-2">
          <div class="flex justify-between items-center">
            <p class="text-green-800 text-sm">Showing full content</p>
            <button 
              class="btn bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600"
              onclick={() => showFullContent = false}
            >
              Back to Preview
            </button>
          </div>
        </div>
      {/if}
      <Highlight language={getLanguage()} code={getProcessedContent()} let:highlighted>
        <LineNumbers {highlighted} />
      </Highlight>
    {/if}
  {:else}
    <div class="markdown-body rounded-base px-4 pb-4 md:px-11 md:pb-11 w-full text-sm">
      {@html file.content}
    </div>
  {/if}
</div>