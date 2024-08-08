<script lang="ts">
  import { type Files  } from "$lib/scripts/types";
  import FileSetup from "$lib/card/FileSetup.svelte";


  /** @type {import('./$types').PageData} */
	export let data;

  let fileInfo: Files  = data.files;
  
  let modifiedAt: string= data.modifiedAt;

  let name: string = data.name;

  let registry: string = data.registry;

  let repository: string = data.repository;

  let version: string = data.version;

  let basePath: string = data.basePath;

  let displayPath: string[] = data.displayPath;

  let subdir: string | null = data.subdir;

  let prevPath: string = data.prevPath;

  
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
