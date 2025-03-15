<script lang="ts">
  
  import type { PageProps } from './$types';
  import Highlight, { LineNumbers } from "svelte-highlight";
  import json from "svelte-highlight/languages/json";
  import python from "svelte-highlight/languages/python";
  import yaml from "svelte-highlight/languages/yaml";
  import sql from "svelte-highlight/languages/sql";
  import atomOneLight from "svelte-highlight/styles/atom-one-light";
  import { convertMarkdown } from '$lib/components/readme/util';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  let { data }: PageProps = $props();
  let rawFile = data.rawFile;
  let splitPath: string[] = data.splitPath;
  let convertedMarkdown: string = $state('')

  export function goBack() {
    history.back();
  }

  function formatJson(jsonString: string): string {
    let newJson = JSON.stringify(JSON.parse(jsonString), null, 2);
    return newJson;
  }

  onMount(async () => {
    if (rawFile.suffix === 'md') {
      convertedMarkdown = await convertMarkdown(rawFile.content);
    }
  });

  function constructPath(index: number): string {
    const basePath = `/opsml/${data.registry.toLowerCase()}/card/files`;
    const dynamicPath = splitPath.slice(4, index + 1).join('/');
    const queryParams = `?repository=${data.metadata.repository}&name=${data.metadata.name}&version=${data.metadata.version}`;
    return dynamicPath ? `${basePath}/${dynamicPath}${queryParams}` : `${basePath}${queryParams}`;
  }

  function gotoPath(index: number) {
    const path = constructPath(index);
    goto(path);

  }

</script>

<svelte:head>
  {@html atomOneLight}
</svelte:head>

<div class="mx-auto w-9/12 pb-10 flex justify-center min-h-screen">
  <div class="w-full pt-4">
    <div class="rounded-lg border-2 border-black shadow overflow-x-auto bg-primary-500 py-2 mb-2 justify-center">
      <h1 class="ml-4 flex flex-row flex-wrap items-center text-lg">
        {#each splitPath as path, index}
          {#if index < 3}
            <div class="group flex flex-none items-center">
              <div class="font-semibold text-black hover:text-secondary-500">{path}</div>
              <div class="mx-0.5 text-gray-800">/</div>
            </div>
          {:else}
            {#if index == splitPath.length - 1}
              <div class="group flex flex-none items-center">
                <div class="font-semibold text-black hover:text-secondary-500">{path}</div>
              </div>
            {:else}
              <div class="group flex flex-none items-center">
                <button class="btn bg-white border-2 border-black shadow-small shadow-hover-small text-black rounded-lg mx-2" onclick={() => gotoPath(index)}>{path}</button>
                <div class="mx-0.5 text-gray-800">/</div>
              </div>
            {/if}
          {/if}

        {/each}
      </h1>

    </div>
    <div class="rounded-lg border-2 border-black shadow overflow-x-auto bg-slate-100 max-h-screen overflow-y-auto">


      {#if rawFile.suffix === 'md'}
      
        <div class="markdown-body rounded-base px-4 pb-4 md:px-11 md:pb-11 w-full">
          {@html convertedMarkdown}
        </div>

      {:else if rawFile.suffix === 'json' || rawFile.suffix === 'jsonl' }

        <div class="w-full">
          <Highlight language={json}  code={formatJson(rawFile.content)} let:highlighted>
            <LineNumbers {highlighted} />
          </Highlight>
        </div>

      {/if}

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