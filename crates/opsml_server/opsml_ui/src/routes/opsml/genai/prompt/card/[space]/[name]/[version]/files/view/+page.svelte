<script lang="ts">
  
  import type { PageProps } from './$types';
  import FileViewPage from '$lib/components/files/FileViewPage.svelte';


  let { data }: PageProps = $props();

</script>

<div class="flex-1 mx-auto max-w-6xl pb-10 px-4">
  <FileViewPage
    file={data.rawFile}
    splitPath={data.splitPath}
    registry={data.registryType}
    space={data.metadata.space}
    name={data.metadata.name}
    version={data.metadata.version}
    />
</div>

