<script lang="ts">
    import { Marked } from 'marked';
    import { markedHighlight } from 'marked-highlight';
    import hljs from 'highlight.js';
    import 'highlight.js/styles/github.css';
    import "github-markdown-css/github-markdown-light.css";
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import type { ReadMe } from '../readme/util';
    import { convertMarkdown } from '../readme/util';
  
    let html = $state('');
  
    let {
        name,
        space,
        registryPath,
        version,
        readMe,
      } = $props<{
        name: string;
        space: string;
        registryPath: string;
        version: string;
        readMe: ReadMe;
      }>();
   
  
    
    function navigateToReadMe() {
        goto(`/opsml/${registryPath}/card/${space}/${name}/${version}/readme`);
      }
  
  
  
    onMount(async () => {
  
      if (readMe.exists) {
        html = await convertMarkdown(readMe.readme);
      }
      
    });
  
  
  </script>
  
  
  <div class="grid justify-items-end py-4 px-4">
    <div>
      <button 
        class="mb-2 text-sm text-black bg-primary-500 rounded-lg shadow shadow-hover border-black border-2 justify-start w-34 h-10"
        onclick={navigateToReadMe}
      >
        Edit ReadMe
      </button>
    </div>
  </div>
  <div class="markdown-body rounded-base px-4 pb-4 md:px-11 md:pb-11 w-full text-sm">
    {@html html}
  </div>
  <style>
  
  
    :global(.markdown-body) {
      box-sizing: border-box;
      margin: 0 auto;
      width: 100%;
      font-size: medium;
    }
  
    :global(.markdown-body pre) {
      overflow-x: auto;
      white-space: nowrap;
    }
  
  </style>