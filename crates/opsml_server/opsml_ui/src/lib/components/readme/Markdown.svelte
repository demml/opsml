<script lang="ts">
    import { Marked } from 'marked';
    import { markedHighlight } from 'marked-highlight';
    import hljs from 'highlight.js';
    import 'highlight.js/styles/github.css';
    import "github-markdown-css/github-markdown-light.css";
    import { onMount } from 'svelte';
  
    let {source} = $props<{source: String}>();
  
    function convertMarkdown(markdown: string) {
        // @ts-ignore
        source = marked.parse(markdown);
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
  
  <div class="mx-auto w-11/12 min-h-screen pt-20 pb-10 m500:pt-14 lg:pt-[100px] flex justify-center">
    <div class="grid grid-cols-1 md:grid-cols-6 gap-4 w-full">
      <div class="col-span-1 md:col-span-4 gap-1 p-4 flex flex-col rounded-base border-black border-2 shadow bg-secondary-100 w-full">
        <div class="markdown-body  p-4 md:p-11 w-full">
            {@html source}
          </div>
      </div>
  
      <div class="col-span-1 md:col-span-2 bg-primary-100 p-4 flex flex-col rounded-base border-black border-2 shadow">
      </div>
    </div>
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