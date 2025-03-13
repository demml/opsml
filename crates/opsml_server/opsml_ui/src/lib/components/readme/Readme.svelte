<script lang="ts">
  import { keymap } from "@codemirror/view";
  import { indentWithTab } from "@codemirror/commands";
  import { basicSetup, EditorView } from "codemirror";
  import { markdown } from "@codemirror/lang-markdown";
  import { languages } from "@codemirror/language-data";
  import { Compartment } from '@codemirror/state';
  import { editorTheme } from './editor-theme';
  import Markdown from "./Markdown.svelte";
  import { onDestroy, onMount } from 'svelte';
  import type { RegistryType } from "$lib/utils";

  let {
      name,
      repository,
      registry,
      content,
    } = $props<{
      name: string;
      repository: string;
      registry: RegistryType;
      content: string;
    }>();


  // State
  let mode = $state('edit');
  let editor: EditorView;

  const themeConfig = new Compartment();

  async function toggle( toggle:string ) {

  if (toggle === 'edit') {
    // show the editor
    //document.getElementById("editor")!.style.display = "block";

    mode = 'edit';

  } else {
    // hide the editor
    //document.getElementById("editor")!.style.display = "none";
    content = editor.state.doc.toString();

    mode = 'preview';
  }

}

  async function saveReadme() {

    // save the content
    content = editor.state.doc.toString();

    let body = {
      name: name,
      repository: repository,
      registry_type: registry,
      content: content
    };
    

      // TODO: Implement save functionality
      console.log('Saving readme:', body);
  }

  onMount(() => {
    let parent = document.getElementById("editor")!;

    editor = new EditorView({
      doc: content,
      extensions: [
        keymap.of([indentWithTab]),
        basicSetup,
        markdown({
          codeLanguages: languages,
          addKeymap: true,
          extensions: []
        }),
        themeConfig.of([editorTheme])
      ],
      parent: parent
    });

  });

  onDestroy(() => {
      if (editor) {
          editor.destroy();
      }
  });

</script>

<div class="flex flex-col">
  <div class="flex px-3 py-2 min-w-96 justify-between border-black border-b-2 pb-4 bg-primary-300">
    <div class="flex gap-4 justify-start">
      <button 
          class="btn btn-md bg-primary-500 border-black border-black border-2 text-black {mode === 'edit' ? '' : 'shadow shadow-hover'}"
          onclick={() => toggle('edit')}
      >
          Edit
      </button>
      <button 
          class="btn btn-md bg-primary-500 border-black border-black border-2 text-black {mode === 'preview' ? '' : 'shadow shadow-hover'}"
          onclick={() => toggle('preview')}
      >
          Preview
      </button>
    </div>

    <div class="justify-end">
      <button 
          type="button" 
          class="btn btn-md bg-primary-500 border-black border-black border-2 text-black shadow shadow-hover" 
          onclick={saveReadme}
        >Save
      </button>
    </div>
  </div>

  <div class="min-w-96 w-full border border-gray overflow-scroll">
    {#if mode === 'edit'}
      <div id="editor"></div>
    {:else}
        <Markdown source={$content} />
    {/if}
  </div>
  
</div>


<style>

:global(#editor) {
      box-sizing: border-box;
      margin: 0 auto;
      width: 100%;
      font-size: large;
    }
</style>