<script lang="ts">
  import { keymap } from "@codemirror/view";
  import { indentWithTab } from "@codemirror/commands";
  import { basicSetup, EditorView } from "codemirror";
  import { markdown } from "@codemirror/lang-markdown";
  import { languages } from "@codemirror/language-data";
  import { Compartment } from '@codemirror/state';
  import { editorTheme } from './editor-theme';
  import {  onMount } from 'svelte';
  import { getRegistryPath, type RegistryType } from "$lib/utils";
  import { convertMarkdown, createReadMe } from "./util";
  import { goto } from "$app/navigation";
  import { getContext } from 'svelte';
  import { type ToastContext } from '@skeletonlabs/skeleton-svelte';

  let error = $state('Failed to save ReadMe');
  export const toast: ToastContext = getContext('toast');

  function triggerError() {
    toast.create({
      title: 'Failed',
      description: error,
      type: 'error'
    });
  }

  function triggerSuccess() {
    toast.create({
      title: 'Success',
      description: 'ReadMe has been saved!',
      type: 'success'
    });
  }

  let {
      name,
      space,
      version,
      registry,
      readme_content,
    } = $props<{
      name: string;
      space: string;
      version: string;
      registry: RegistryType;
      readme_content: string;
    }>();


  // State
  let mode = $state('edit');
  let editor: EditorView;

  let content: string = $state('');
  let html_content: string = $state('');

  const themeConfig = new Compartment();


  async function saveReadme() {
    content = editor.state.doc.toString();
    let response = await createReadMe(name, space, registry, content);

    if (!response.uploaded) {
      error = response.message;
      triggerError();
    } else {
      triggerSuccess();
    }

    goto(`/opsml/${getRegistryPath(registry)}/card/${space}/${name}/${version}/card`);
  }

async function toggle(toggle: string) {
  mode = toggle;
  
  if (toggle === 'preview') {
    content = editor.state.doc.toString();
    html_content = await convertMarkdown(content);
  }
}



  onMount(() => {
    content = readme_content;
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

</script>

<div class="flex flex-col rounded-base w-full overflow-auto">
  <div class="flex px-3 py-2 min-w-96 rounded-t-base justify-between border-b-2 border-black pb-4 bg-primary-300">
    <div class="flex gap-4 justify-start">
      <button 
          class="btn text-sm bg-primary-500 border-black border-black border-2 text-black {mode === 'edit' ? '' : 'shadow shadow-hover'}"
          onclick={() => toggle('edit')}
      >
          Edit
      </button>
      <button 
          class="btn text-sm bg-primary-500 border-black border-black border-2 text-black {mode === 'preview' ? '' : 'shadow shadow-hover'}"
          onclick={() => toggle('preview')}
      >
          Preview
      </button>
    </div>

    <div class="justify-end">
      <button 
          type="button" 
          class="btn text-sm bg-primary-500 border-black border-black border-2 text-black shadow shadow-hover" 
          onclick={saveReadme}
        >Save
      </button>
    </div>
  </div>

  <div class="min-w-96 w-full overflow-hidden relative">
    <div id="editor" 
         class="h-full overflow-y-auto pt-4" 
         style="display: {mode === 'edit' ? 'block' : 'none'}">
    </div>
    {#if mode === 'preview'}
      <div class="markdown-body p-4 md:p-11 w-full h-full overflow-y-auto rounded-base text-sm">
        {@html html_content}
      </div>
    {/if}
  </div>
  
</div>


<style>

:global(#editor) {
      box-sizing: border-box;
      margin: 0 auto;
      width: 100%;
      font-size: 14px;
    }

:global(.markdown-body) {
  box-sizing: border-box;
  margin: 0 auto;
  width: 100%;
  font-size: medium;
  max-height: 100%;
}

:global(.markdown-body pre) {
  overflow-x: auto;
  white-space: nowrap;
}
</style>