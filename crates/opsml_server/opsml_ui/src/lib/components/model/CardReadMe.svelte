<script lang="ts">
  import { Marked } from 'marked';
  import { markedHighlight } from 'marked-highlight';
  import hljs from 'highlight.js';
  import 'highlight.js/styles/github.css';
  import "github-markdown-css/github-markdown-light.css";
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { getRegistryTypeLowerCase, type RegistryType } from '$lib/utils';

  let html = $state('');

  let {
      name,
      repository,
      registry,
      version,
      content,
    } = $props<{
      name: string;
      repository: string;
      version: string;
      registry: RegistryType;
      content: string;
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
      let test = `
# My Data Readme

## Summary

This is an example summary for a model

### Features:
- Feature 1
- Feature 2

### Model parameters:
- Parameter 1
- Parameter 2

### Model output:
- Output 1
- Output 2

### Model usage:
- **Usage 1**
- Usage 2

### Example code:

\`\`\`python
import numpy as np
from opsml import CardRegistry, ModelCard

# Create a new card registry

registry = CardRegistry()

a = 10

class Hello:
	def __init__(self, a):
	

\`\`\`
        `;

      convertMarkdown(test);
  });
</script>

  <div class="grid justify-items-end py-4 px-4">
    <div >
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