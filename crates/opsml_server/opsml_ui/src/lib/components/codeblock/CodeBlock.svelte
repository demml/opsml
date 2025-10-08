<script module>
  import { createHighlighterCoreSync } from 'shiki/core';
  import { createJavaScriptRegexEngine } from 'shiki/engine/javascript';
  import { customTheme } from './customTheme';

  import console from 'shiki/langs/console.mjs';
  import html from 'shiki/langs/html.mjs';
  import css from 'shiki/langs/css.mjs';
  import js from 'shiki/langs/javascript.mjs';
  import python from 'shiki/langs/python.mjs';
  import rust from 'shiki/langs/rust.mjs';
  import json from 'shiki/langs/json.mjs';
  import md from 'shiki/langs/markdown.mjs';


  const shiki = createHighlighterCoreSync({
    engine: createJavaScriptRegexEngine(),
    themes: [customTheme],
    langs: [console, html, css, js, python, rust, json, md]
  });
</script>

<script lang="ts">
  import type { CodeBlockProps } from './types';

  let {
    code = '',
    lang = 'console',
    theme = 'custom-light',
    showLineNumbers = false,
    // Base Style Props
    base = 'w-full',
    shadow = '',
    classes = '',
    // Pre Style Props
    preBase = '[&>pre]:w-full [&>pre]:min-w-0',
    prePadding = '[&>pre]:p-4',
    preClasses = '[&>pre]:whitespace-pre [&>pre]:overflow-x-auto'
  }: CodeBlockProps = $props();

  // Shiki convert to HTML
  const generatedHtml = shiki.codeToHtml(code, { lang, theme });
</script>

<div class="w-full {base} {shadow} {classes} {preBase} {prePadding} {preClasses}" class:show-line-numbers={showLineNumbers}>
  {@html generatedHtml}
</div>

<style>

  :global(.shiki) {
    width: 100% !important;
    max-width: 100%;
    display: block;
  }
  
  :global(.shiki pre) {
  width: 100% !important;
  max-width: 100%;
  margin: 0;
  white-space: pre !important;
  overflow-x: auto !important;
  line-height: 0.8 !important;
  font-family: Menlo, Monaco, "Liberation Mono", "Consolas", monospace;
}
  
  :global(.shiki code) {
    width: max-content;
    min-width: 100%;
    display: block;
    white-space: pre !important;
    line-height: 0.8 !important;
  }

  .show-line-numbers :global(.shiki code) {
    counter-reset: step;
    counter-increment: step 0;
  }

  .show-line-numbers :global(.shiki .line) {
    display: block;
    position: relative;
    line-height: 0.8 !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  .show-line-numbers :global(.shiki .line::before) {
    content: counter(step);
    counter-increment: step;
    width: 1.5rem;
    margin-right: 0.25rem;
    display: inline-block;
    text-align: right;
    color: rgba(115, 138, 148, 0.7);
    font-variant-numeric: tabular-nums;
    user-select: none;
    border-right: 1px solid rgba(115, 138, 148, 0.2);
    padding-right: 0.125rem;
    line-height: 0.8 !important;
  }
</style>