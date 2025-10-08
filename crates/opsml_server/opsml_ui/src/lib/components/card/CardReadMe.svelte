<script lang="ts">
  import 'highlight.js/styles/github.css';
  import "github-markdown-css/github-markdown-light.css";
  import { onMount } from 'svelte';
  import type { ReadMe } from '../readme/util';
  import { convertMarkdown } from '../readme/util';
  import { getRegistryPath, type RegistryType } from '$lib/utils';
  
    let html = $state('');
  
    let {
        name,
        space,
        registryType,
        version,
        readMe,
      } = $props<{
        name: string;
        space: string;
        registryType: RegistryType;
        version: string;
        readMe: ReadMe;
      }>();
   
  
    
   

    let readMeUrl = $state(`/opsml/${getRegistryPath(registryType)}/card/${space}/${name}/${version}/readme`);
  
  
  
    onMount(async () => {
  
      if (readMe.exists) {
        html = await convertMarkdown(readMe.readme);
      }
      
    });
  
  
  </script>
  
  
  <div class="grid justify-items-end py-4 px-4">
    <div>
      <a 
        class="btn mb-2 text-sm text-black bg-primary-500 rounded-lg shadow shadow-hover border-black border-2 p-4"
        href={readMeUrl}
        data-sveltekit-preload-data="hover"
      >
        Edit ReadMe
      </a>
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