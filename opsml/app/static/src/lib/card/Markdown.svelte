<script lang="ts">

import { onMount } from 'svelte';

import { Marked } from "marked";
import { markedHighlight } from "marked-highlight";
import {markedEmoji} from "marked-emoji";
import hljs from 'highlight.js';
import {Octokit} from "@octokit/rest";

export let source: string;
export let globalPadding: string = "45px";
export let globalPaddingMobile: string = "15px";

const octokit = new Octokit();

const marked = new Marked(
  markedHighlight({
    langPrefix: 'hljs language-',
    highlight(code, lang, info) {
      const language = hljs.getLanguage(lang) ? lang : 'plaintext';
      return hljs.highlight(code, { language }).value;
    }
  })
);


// inject the html into the markdown component
onMount(async () => {

  const emojis = await octokit.rest.emojis.get().then(response => response.data);
  
  const options = {
    emojis,
    renderer: (token) => `<img class="marked-emoji-img" style="width:1em;display:inline;" alt="${token.name}" src="${token.emoji}">`
  };

  marked.use(markedEmoji(options));

	let html = await marked.parse(source);
  let mkdown = document.getElementById('markdown')!;
  let mkdownDiv = document.createElement('article');
  mkdownDiv.classList.add("markdown-body");

  // update padding if size

  if (window.innerWidth < 768) {
    mkdownDiv.style.padding = globalPaddingMobile;
  } else {
    mkdownDiv.style.padding = globalPadding;
  }

  mkdownDiv.innerHTML = html;
  mkdown.appendChild(mkdownDiv);

});



</script>

  <div id="markdown">

  </div>

  <style>

	:global(.markdown-body) {
		box-sizing: border-box;
		margin: 0 auto;
	}

</style>