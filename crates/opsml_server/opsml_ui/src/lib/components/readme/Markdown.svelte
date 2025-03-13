<script lang="ts">
    import { Marked } from 'marked';
    import { markedHighlight } from 'marked-highlight';
    import hljs from 'highlight.js';
    import 'highlight.js/styles/github.css';
    import "github-markdown-css/github-markdown-light.css";
    import { onMount } from 'svelte';
  
    let {source} = $props<{source: String}>();
    let html_source = $state('');
  
    function convertMarkdown(markdown: string) {
        // @ts-ignore
        html_source = marked.parse(markdown);
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
        convertMarkdown(source);
    });


  </script>
  
    {@html html_source}
 
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