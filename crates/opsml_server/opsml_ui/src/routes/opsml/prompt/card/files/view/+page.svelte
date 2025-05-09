<script lang="ts">
  
  import type { PageProps } from './$types';
  import FileViewPage from '$lib/components/files/FileViewPage.svelte';


  let { data }: PageProps = $props();

</script>

<div class="flex-1 mx-auto w-9/12 pb-10 flex justify-center overflow-auto px-4">
  <FileViewPage
    file={data.rawFile}
    splitPath={data.splitPath}
    registry={data.registry.toLocaleLowerCase()}
    space={data.metadata.space}
    name={data.metadata.name}
    version={data.metadata.version}
    />
</div>

