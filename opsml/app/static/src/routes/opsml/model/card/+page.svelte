<script lang="ts">

  import { TabGroup, Tab } from '@skeletonlabs/skeleton';
  import Fa from 'svelte-fa'
  import { faTag, faIdCard, faFolderOpen } from '@fortawesome/free-solid-svg-icons'
  import { onMount } from 'svelte';
  import { keymap } from "@codemirror/view"


  import { indentWithTab } from "@codemirror/commands"
  import {basicSetup, EditorView} from "codemirror"
  import {markdown} from "@codemirror/lang-markdown"
  import {languages} from "@codemirror/language-data"
  import { Compartment } from '@codemirror/state'
  import Search from "$lib/Search.svelte";
  import icon from '$lib/images/opsml-green.ico'

  
  import { editorTheme } from '$lib/scripts/editor_theme'
  import { type ModelMetadata } from "$lib/scripts/types";
  import CardBadge from "$lib/CardBadge.svelte";


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

  let searchTerm: string | undefined = undefined;

  let searchVersions = (e) => {
    searchTerm = e.target.value;
  }


  

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

  <div class="pl-4 md:pl-20 pt-6 sm:pt-8 bg-slate-50 w-full pb-8 border-b">
    <h1 class="flex flex-row flex-wrap items-center text-lg">
      <div class="group flex flex-none items-center">
        <a class="font-semibold text-gray-800 hover:text-secondary-500" href="/opsml/{registry}?repository={repository}">{repository}</a>
        <div class="mx-0.5 text-gray-800">/</div>
      </div>
      <div class="font-bold text-primary-500">{name}</div>
      <div class="ml-4 w-1/3">
        <Search bind:searchTerm on:input={searchVersions} placeholder="Filter versions"/>
      </div>
    </h1>
    <div class="pt-2 flex flex-wrap flex-row items-center gap-3">
      <div>
        <a href="/opsml/{registry}/card?name={name}&repository={repository}&version={metadata.model_version}" class="badge h-7 border border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100">
          <Fa class="h-7" icon={faTag} color="#4b3978"/>
          <span class="text-primary-500">{metadata.model_version}</span>
        </a>
      </div>
    </div>
  </div>

  
  <div class="flex flex-wrap">
    <div class="w-full md:w-2/3 border-r border-grey-100 pl-4 md:pl-20">
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
    <div class="w-full md:w-1/3 mt-5 pl-4">
      <div class="pl-4">
        <header class="mb-2 text-lg font-bold">Metadata</header>

        <!-- UID -->
        <div class="flex flex-row gap-1 items-center">
          <div class="w-8">
            <Fa class="h-12" icon={faIdCard} color="#04cd9b"/>
          </div>
          <div class="w-32 font-semibold text-gray-500">ID:</div>
          <div class="w-48 ">0uyoiulkjhoiuho</div>
        </div>

        <!-- name -->
        <div class="flex flex-row gap-1 items-center">
          <div class="w-8">
            <Fa class="h-12" icon={faIdCard} color="#04cd9b"/>
          </div>
          <div class="w-32 font-semibold text-gray-500">Name:</div>
          <div class="w-48 ">{metadata.model_name}</div>
        </div>

        <!-- version -->
        <div class="flex flex-row gap-1 items-center">
          <div class="w-8">
            <Fa class="h-12" icon={faIdCard} color="#04cd9b"/>
          </div>
          <div class="w-32 font-semibold text-gray-500">Version:</div>
          <div class="w-48 ">{metadata.model_version}</div>
        </div>


        <!-- repository -->
        <div class="flex flex-row gap-1 items-center">
          <div class="w-8">
            <Fa class="h-12" icon={faFolderOpen} color="#04cd9b"/>
          </div>
          <div class="w-32 font-semibold text-gray-500">Respository:</div>
          <div class="w-48 ">{metadata.model_repository}</div>
        </div>

      </div>
      
    </div>

  </div>
  


  


</div>
