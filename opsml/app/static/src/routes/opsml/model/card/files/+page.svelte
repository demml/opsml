<script lang="ts">
  import FileSystem from "$lib/card/FileSystem.svelte";


  /** @type {import('./$types').PageData} */
	export let data;

  let tabSet: string = "files";

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


</script>

<div class="flex flex-wrap">
  <div class="w-full md-full px-4 pt-8 md:px-20 text-sm">
    <div class="bg-gradient-to-b from-primary-50 to-white flex rounded-t-lg border border-gray px-3 py-2 min-w-96">
      <div class="inline-flex justify-between w-full items-center">
        <div class="text-primary-500 font-semibold">Files for {name}</div>
        <div class="text-gray-500"> {modifiedAt}</div>
      </div>
    </div>

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
