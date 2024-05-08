<script lang="ts">
    import FileView from "$lib/card/FileView.svelte";
    import { type ViewContent, type FileInfo } from "$lib/scripts/types";
    import { onMount } from 'svelte';
    import { keymap } from "@codemirror/view"
  
    import { editorTheme } from '$lib/scripts/editor_theme'
    import { calculateTimeBetween } from "$lib/scripts/utils";
  
  
    
    /** @type {import('./$types').PageData} */
      export let data;
      
      let fileInfo: FileInfo;
      $: fileInfo = data.file_info;
  
      let content: ViewContent;
      $: content = data.content;
    
    
    </script>
  
  
  <FileView
    name={fileInfo.name}
    modifiedAt={calculateTimeBetween(fileInfo.mtime)}
    viewType={content.view_type}
    content={content.content}
    uri={fileInfo.uri}
    suffix={fileInfo.suffix.replace('.', '')}
  />