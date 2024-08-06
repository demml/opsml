<script lang="ts">
  import { type Files  } from "$lib/scripts/types";
  import FileSetup from "$lib/card/FileSetup.svelte";


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

  let subdir: string | null;
  $: subdir = data.subdir;

  let prevPath: string;
  $: prevPath = data.prevPath;

  
</script>

<FileSetup
  registry={registry}
  name={name}
  repository={repository}
  version={version}
  basePath={basePath}
  displayPath={displayPath}
  modifiedAt={modifiedAt}
  subdir={subdir}
  fileInfo={fileInfo}
  prevPath={prevPath}
/>
