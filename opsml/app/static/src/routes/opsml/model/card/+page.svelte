<script lang="ts">

  import { TabGroup, Tab } from '@skeletonlabs/skeleton';
  import Fa from 'svelte-fa'
  import { faTag } from '@fortawesome/free-solid-svg-icons'
  import { onMount } from 'svelte';
  import { keymap } from "@codemirror/view"


  import { indentWithTab } from "@codemirror/commands"
  import {basicSetup, EditorView} from "codemirror"
  import {markdown} from "@codemirror/lang-markdown"
  import {languages} from "@codemirror/language-data"
  import { Compartment } from '@codemirror/state'
  import icon from '$lib/images/opsml-green.ico'
  import sklearnLogo from '$lib/images/scikit-learn.svg'
  
  import { editorTheme } from '$lib/scripts/editor_theme'
  import { type ModelMetadata } from "$lib/scripts/types";


  /** @type {import('./$types').PageData} */
	export let data;

  let registry: string;
  $: registry = data.registry;

  let name: string;
  $: name = data.name;

  let repository: string;
  $: repository = data.repository;

  let metadata: ModelMetadata;
  $: metadata = data.metadata;

  let hasReadme: boolean;
  $: hasReadme = data.hasReadme;


  

  onMount(async () => {
    const themeConfig = new Compartment()

    let parent = document.getElementById("editor")
		let editor = new EditorView({
      doc: ``,
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
    })
	});


</script>

<div class="flex flex-1 flex-col">

  <div class="pl-12 sm:pl-20 pt-6 sm:pt-8 bg-slate-50 w-full pb-8 border-b">
    <h1 class="flex flex-row flex-wrap ... items-center text-lg">
      <div class="group flex flex-none items-center">
        <a class="font-semibold text-gray-800 hover:text-secondary-500" href="/opsml/{registry}?repository={repository}">{repository}</a>
        <div class="mx-0.5 text-gray-800">/</div>
      </div>
      <div class="font-bold text-primary-500">{name}</div>
    </h1>
    <div class="pt-2 flex flex-wrap flex-row items-center gap-3">
      <div>
        <a href="/opsml/{registry}/card?name={name}&repository={repository}&version={metadata.model_version}" class="badge h-7 bg-surface-100 border border-surface-300 hover:bg-gradient-to-b from-surface-50 to-primary-100">
          <Fa class="h-7" icon={faTag} color="#4b3978"/>
          <span class="text-primary-500">{metadata.model_version}</span>
        </a>
      </div>

      {#if metadata.model_interface === 'SklearnModel'}
      <div>
        <a class="badge bg-surface-100 border border-surface-300 hover:bg-gradient-to-b from-surface-50 to-primary-100">
          <img alt="sklearn logo" class="h-5" src="{sklearnLogo}">
          <span class="text-primary-500">{metadata.model_interface}</span>
        </a>
      </div>
      {:else if metadata.model_interface === 'TensorflowModel'}


      {/if}
    </div>
  </div>


  <div class="flex flex-row flex-initial">
    <div class="w-2/3 border-r border-grey-100 pl-12 sm:pl-20 ">
      {#if !hasReadme}
        <div class="mt-5 mr-5 py-24 bg-gradient-to-b from-secondary-50 to-white rounded-lg text-center items-center">
          <p class="mb-1">No card README found</p>
          <p class="mb-1 text-sm text-gray-500">Click button below to create a README!</p>
          <p class="mb-6 text-sm text-gray-500">Note: README applies to all versions of a given model and repository </p>
          <button type="button" class="btn variant-filled">
            <img class="h-5" alt="The project logo" src={icon} />
            <span>Button</span>
          </button>
        </div>
        {:else}
          <div id="editor" class="h-96"></div>
      {/if}
    </div>
    <div class="flex flex-row flex-wrap w-1/3 mt-5">
      <div class="px-8">
        <header class="text-lg font-bold">Metadata</header>
      </div>
    </div>

  </div>
  


  


</div>
