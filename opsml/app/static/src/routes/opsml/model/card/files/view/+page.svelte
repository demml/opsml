<script lang="ts">
  import FileView from "$lib/card/FileView.svelte";
  import { type ViewContent, type FileInfo } from "$lib/scripts/types";
  import { onMount } from 'svelte';
  import { keymap } from "@codemirror/view"


  import { indentWithTab } from "@codemirror/commands"
  import {basicSetup, EditorView} from "codemirror"
  import { EditorState, Compartment } from "@codemirror/state"
  import {markdown} from "@codemirror/lang-markdown"
  import {languages} from "@codemirror/language-data"
  import { json } from "@codemirror/lang-json";
  import { editorTheme } from '$lib/scripts/editor_theme'
  import { calculateTimeBetween } from "$lib/scripts/utils";
  
  /** @type {import('./$types').PageData} */
    export let data;
    
    let fileInfo: FileInfo;
    $: fileInfo = data.file_info;

    let content: ViewContent;
    $: content = data.content;


  onMount(async () => {
    const themeConfig = new Compartment()

    let parent = document.getElementById("editor")

    console.log(content.view_type);

    let parsed = JSON.parse(content.content);

    if (content.view_type === 'code') {
      let editor = new EditorView({
        doc: JSON.stringify(parsed),
        extensions: [
          basicSetup,
          json(),
          themeConfig.of([editorTheme]),
          EditorState.readOnly.of(true),
          EditorView.lineWrapping 
        ],
        parent: parent
      })
    }
  });
  
  
  </script>


<FileView
  name={fileInfo.name}
  modifiedAt={calculateTimeBetween(fileInfo.mtime)}
  viewType={content.view_type}
  content={content.content}
/>
  