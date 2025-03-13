<script lang="ts">
  import { Marked } from 'marked';
  import { markedHighlight } from 'marked-highlight';
  import hljs from 'highlight.js';
  import 'highlight.js/styles/github.css';
  import "github-markdown-css/github-markdown-light.css";
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { getRegistryTypeLowerCase, type RegistryType } from '$lib/utils';
  import type { ReadMe } from '../readme/util';

  let html = $state('');

  let {
      name,
      repository,
      registry,
      version,
      readMe,
    } = $props<{
      name: string;
      repository: string;
      version: string;
      registry: RegistryType;
      readMe: ReadMe;
    }>();
 

  function convertMarkdown(markdown: string) {
      // @ts-ignore
      html = marked.parse(markdown);
  }

  function navigateToReadMe() {
    console.log('navigate to readme');
      // navigate to the card page
      let registry_name = getRegistryTypeLowerCase(registry);
      goto(`/opsml/${registry_name}/card/readme?name=${name}&repository=${repository}&version=${version}`);
    }

  // Configure marked with markedHighlight
  const marked = new Marked(
      markedHighlight({
          langPrefix: 'hljs language-',
          highlight(code, lang) {
              const language = hljs.getLanguage(lang) ? lang : 'plaintext';
              return hljs.highlight(code, { language }).value;
          }
      })
  );

 

  onMount(() => {


    if (readMe.exists) {
      convertMarkdown(readMe.content);
    }
    
  });


</script>

{#if readMe.exists}
  <div class="grid justify-items-end py-4 px-4">
    <div>
      <button 
        class="mb-2 text-black bg-primary-500 rounded-lg shadow shadow-hover border-black border-2 justify-start w-38 h-10"
        onclick={navigateToReadMe}
      >
        edit ReadMe
      </button>
    </div>
  </div>
  <div class="markdown-body rounded-base px-4 pb-4 md:px-11 md:pb-11 w-full">
    {@html html}
  </div>
{:else}
  <div class="grid justify-items-end py-4 px-4">
    <div>
      <button 
        class="mb-2 text-black bg-primary-500 rounded-lg shadow shadow-hover border-black border-2 justify-start w-38 h-10"
        onclick={navigateToReadMe}
      >
        add ReadMe
      </button>
    </div>
  </div>
  <div class="markdown-body rounded-base px-4 pb-4 md:px-11 md:pb-11 w-full">
    <p class="text-center text-lg text-gray-500">No ReadMe found</p>
  </div>
{/if}

<style>


  :global(.markdown-body) {
    box-sizing: border-box;
    margin: 0 auto;
    width: 100%;
    font-size: large;
  }

  :global(.markdown-body pre) {
    overflow-x: auto;
    white-space: nowrap;
  }



</style>