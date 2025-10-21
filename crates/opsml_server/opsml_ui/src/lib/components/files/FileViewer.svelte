<script lang="ts">
  import type { RawFile } from "./types";
  import { getFileTypeInfo } from './utils';
  import ImageViewer from './ImageViewer.svelte';
  import MarkdownViewer from './MarkdownViewer.svelte';
  import CodeViewer from './CodeViewer.svelte';

  /**
   * Main file viewer component that routes to appropriate specialized viewers
   */
  interface Props {
    file: RawFile;
  }

  let { file }: Props = $props();
  
  const fileTypeInfo = $derived(getFileTypeInfo(file.suffix, file.mime_type));

</script>

<div class="h-full text-sm overflow-auto">
  {#if fileTypeInfo.type === 'image'}
    <ImageViewer mimeType={file.mime_type} content={file.content} />
    
  {:else if fileTypeInfo.type === 'markdown'}
    <MarkdownViewer content={file.content} />
    
  {:else if fileTypeInfo.type === 'code'}

    <CodeViewer content={file.content} language={fileTypeInfo.language} />
  
    
  {:else}
    <div class="markdown-body rounded-base px-4 pb-4 md:px-11 md:pb-11 w-full text-sm">
      {@html file.content}
    </div>
  {/if}
</div>