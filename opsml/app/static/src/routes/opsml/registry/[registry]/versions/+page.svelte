<script lang="ts">

  import { TabGroup, Tab } from '@skeletonlabs/skeleton';
  import Fa from 'svelte-fa'
  import { faTag } from '@fortawesome/free-solid-svg-icons'
  import { onMount } from 'svelte';
  import { basicSetup } from 'codemirror'
  import {EditorView, keymap} from "@codemirror/view"
  import { markdown } from '@codemirror/lang-markdown'
  import { languages } from '@codemirror/language-data'
  import {indentWithTab} from "@codemirror/commands"
  import { markdownLanguage } from '@codemirror/lang-markdown'
  import { Compartment } from '@codemirror/state'
  import testDoc from '$lib/scripts/markdown_template.ts'
  import editorTheme from '$lib/scripts/editor_theme.ts'
  import { type ModelMetadata } from "$lib/scripts/types";


  /** @type {import('./$types').PageData} */
	export let data;

  let registry: string;
  $: registry = data.registry;

  let name: string;
  $: name = data.name;

  let repository: string;
  $: repository = data.repository;

  let path: string;
  $: path = data.path;

  let metadata: ModelMetadata;
  $: metadata = data.metadata;

  

  onMount(async () => {
    const themeConfig = new Compartment()

    let parent = document.getElementById("editor")
		let editor = new EditorView({
      doc: `# hello`,
      extensions: [
        keymap.of([indentWithTab]),
        basicSetup,
        markdown({
          base: markdownLanguage,
          codeLanguages: languages,
          addKeymap: true,
          extensions: []
        }),
        themeConfig.of([editorTheme])
      ],
      parent: parent
    })
	});


</script>

<div class="flex flex-1 flex-col">

  <div class="pl-12 sm:pl-20 pt-6 sm:pt-8 bg-slate-50 w-full">
    <h1 class="flex flex-row ... items-center text-lg">
      <div class="group flex flex-none items-center">
        <a class="font-semibold text-gray-800 hover:text-secondary-500" href="/opsml/registry/{path}?respository={repository}">{repository}</a>
        <div class="mx-0.5 text-gray-800">/</div>
      </div>
      <div class="font-bold text-primary-500">{name}</div>
    </h1>
    <div class="pt-2 flex flex-wrap flex-row ... items-center">
      <div>
        <a href="/opsml/registry/{path}/versions?name={name}&repository={repository}&version={metadata.version}" class="badge w-16 bg-surface-100 border border-surface-300 hover:bg-gradient-to-b from-surface-50 to-primary-100">
          <Fa icon={faTag} color="#4b3978"/>
          <span class="text-primary-500">{metadata.version}</span>
        </a>
      </div>
    </div>
  </div>

  <div class="ml-12 mt-6 overflow-hidden rounded-lg">
    <div class="flex flex-row flex-initial w-2/3 ... items-center">

      <div class="card w-full border border-slate-100">
        <header class="card-header h-6 mb-4 ">Editor</header>
        <section class="bg-slate-50 border border-slate-20">
          <div id="editor" class="w-full"></div>
        </section>
      </div>

    </div>
     
  </div>
  


  


</div>
