<script lang="ts">
  import FileSystem from "$lib/card/FileSystem.svelte";
  import { type Files  } from "$lib/scripts/types";
  import Fa from 'svelte-fa'
  import { faFolder } from '@fortawesome/free-solid-svg-icons'
  import { goto } from '$app/navigation';

  /** @type {import('./$types').PageData} */
	export let data;

  let fileInfo: Files;
  $: fileInfo = data.files;
  
  let modifiedAt: string;
  $: modifiedAt = data.modifiedAt;

  let name: string;
  $: name = data.name;

  let registry: string;
  $: registry = data.registry;

  let repository: string;
  $: repository = data.repository;

  let version: string;
  $: version = data.version;

  let basePath: string;
  $: basePath = data.basePath;

  let displayPath: string[];
  $: displayPath = data.displayPath;

  let subdir: string | undefined;
  $: subdir = data.subdir;

  let prevPath: string;
  $: prevPath = data.prevPath;


  function navigateToFolder(folderPath: string) {
    let subDir: string = folderPath.replace(`${basePath}/`, '');
    goto(`/opsml/${registry}/card/files?name=${name}&repository=${repository}&version=${version}&subdir=${subDir}`);
  }

  function navigateBreadcrumb(index: number) {
    if (index >= 3) {
      let subDir: string = displayPath.slice(3, index + 1).join('/');
      void goto(`/opsml/${registry}/card/files?name=${name}&repository=${repository}&version=${version}&subdir=${subDir}`);
    } else {
      void goto(`/opsml/${registry}/card/files?name=${name}&repository=${repository}&version=${version}`);
    }
  }
  
</script>

<div class="flex items-center justify-center pt-4 text-sm">
  
    <div class="justify-center w-2/3">
  
      <ol class="breadcrumb pl-2 pb-2">
        {#each displayPath as path, index}
  
        {#if index !== displayPath.length - 1}
          <li class="crumb"><button class="anchor font-semibold" on:click={() => navigateBreadcrumb(index)}>{path}</button></li>
          <li class="crumb-separator" aria-hidden>/</li>
        {:else}
          <li class="crumb"><button class="anchor font-semibold text-secondary-500" on:click={() => navigateBreadcrumb(index)}>{path}</button></li>
        {/if}
        {/each}
      </ol>
  
      <div class="bg-surface-100 to-white flex rounded-t-lg border border-gray px-3 py-2 min-w-96">
        <div class="inline-flex justify-between w-full items-center">
          <div class="text-primary-500 font-semibold">Files for {name}</div>
          <div class="text-primary-500"> {modifiedAt}</div>
        </div>
      </div>
  
      {#if subdir}
      <div class="w-full bg-white border border-gray-200 px-3 py-2 min-w-96">
        <div class="grid h-6 grid-cols-12 gap-x-3">
  
          <!-- svelte-ignore a11y-invalid-attribute -->
          <a class="flex flex-row col-span-8 md:col-span-4 items-center cursor-pointer hover:underline" href="#" role="button" on:click={() => navigateToFolder(prevPath)}>
            <Fa class="h-5 mr-2" icon={faFolder} color="#4b3978"/>
            <div class="flex truncate items-center text-black">..</div>
          </a>
        </div>
      </div>
      {/if}
  
      <FileSystem
        basePath={basePath}
        fileInfo={fileInfo}
        name={name}
        registry={registry}
        repository={repository}
        version={version}
      />
  
    </div>
  </div>
