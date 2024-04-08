<script lang="ts">
  import FileView from "$lib/card/FileView.svelte";
  import { type ViewContent, type FileInfo } from "$lib/scripts/types";
  import { onMount } from 'svelte';
  import { keymap } from "@codemirror/view"

  import { editorTheme } from '$lib/scripts/editor_theme'
  import { calculateTimeBetween } from "$lib/scripts/utils";

  import hljs from 'highlight.js/lib/core';
  import json from 'highlight.js/lib/languages/json';
  hljs.registerLanguage('json', json);

  
  /** @type {import('./$types').PageData} */
    export let data;
    
    let fileInfo: FileInfo;
    $: fileInfo = data.file_info;

    let content: ViewContent;
    $: content = data.content;


  onMount(async () => {
    const themeConfig = new Compartment()

    let parent = document.getElementById("editor")
    html = hljs.highlight('<h1>Hello World!</h1>', {language: 'json'}).value
    parent.innerHTML = html

  });
  
  
  </script>


<FileView
  name={fileInfo.name}
  modifiedAt={calculateTimeBetween(fileInfo.mtime)}
  viewType={content.view_type}
  content={content.content}
/>
  