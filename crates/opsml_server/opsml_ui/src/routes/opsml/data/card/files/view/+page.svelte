<script lang="ts">
  
  import type { PageProps } from './$types';
  import FileViewPage from '$lib/components/files/FileViewPage.svelte';


  let { data }: PageProps = $props();

</script>

<FileViewPage
  file={data.rawFile}
  splitPath={data.splitPath}
  registry={data.registry.toLocaleLowerCase()}
  repository={data.metadata.repository}
  name={data.metadata.name}
  version={data.metadata.version}
  />

