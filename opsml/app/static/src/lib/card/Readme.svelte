<script lang="ts">

  import { keymap } from "@codemirror/view"
  import { indentWithTab } from "@codemirror/commands"
  import {basicSetup, EditorView} from "codemirror"
  import {markdown} from "@codemirror/lang-markdown"
  import {languages} from "@codemirror/language-data"
  import { Compartment } from '@codemirror/state'
  import { editorTheme } from '$lib/scripts/editor_theme'
  import { onMount } from 'svelte';
  import atomOneLight from "svelte-highlight/styles/atom-one-light";
  import Markdown from "$lib/card/Markdown.svelte";
  import { TabGroup, Tab } from '@skeletonlabs/skeleton';
  import { getToastStore, type ToastSettings } from '@skeletonlabs/skeleton';
  import { goto } from '$app/navigation';
  import { apiHandler } from "$lib/scripts/apiHandler";
  import { CommonPaths } from "$lib/scripts/types";


  const themeConfig = new Compartment()
  let editor: EditorView;

  // toast
  const toastStore = getToastStore();

  export let content: string;
  export let name: string;
  export let registry: string;
  export let repository: string;
  export let version: string;
  export let tabSet: string;
  export let status: string;


  async function toggle( toggle:string ) {

    if (toggle === 'edit') {
      // show the editor
      document.getElementById("editor")!.style.display = "block";

      status = 'edit';

    } else {
      // hide the editor
      document.getElementById("editor")!.style.display = "none";

      content = editor.state.doc.toString();

      status = 'preview';
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

    // pass content to server
    let result = await apiHandler.post(CommonPaths.README, body);
    
    // check the result is true
    let message: string ;
    if (result.ok) {
      message = 'Readme saved';
    } else {
      message = "Failed to save readme. Check server logs"
    }

    const t: ToastSettings = {
      message: message,
    };
    toastStore.trigger(t);

    goto(`/opsml/${registry}/card/home/?name=${name}&repository=${repository}&version=${version}`);
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

</script>

<svelte:head>
  {@html atomOneLight}
</svelte:head>

<div class="flex items-center justify-center pt-8">
  <div class="justify-center w-3/4">
    <div class="flex rounded-t-lg border border-gray px-3 py-2 min-w-96 justify-between ">
      
      <TabGroup
        border=""
        active='border-b-2 border-primary-500'
        >
        <Tab bind:group={tabSet} name="edit" value="edit" on:click={() => toggle("edit")}>
          <div class="font-semibold">Edit</div>
        </Tab>

        <Tab bind:group={tabSet} name="preview" value="preview" on:click={() => toggle("preview")}>
          <div class="font-semibold">Preview</div>
        </Tab>

      </TabGroup>

      <div>
        <button type="button" class="btn bg-primary-500 text-white" on:click={() => { saveReadme() }}>
          <span>Save</span>
        </button>
      </div>
      
    </div>

    <div class="min-w-96 w-full border border-gray overflow-scroll">
      <div id="editor"></div>

      {#if status === 'preview'}
        <Markdown source={content} />
      {/if}

    </div>
  </div>
</div>
