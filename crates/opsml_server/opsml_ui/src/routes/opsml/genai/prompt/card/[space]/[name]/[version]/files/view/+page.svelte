<script lang="ts">
  
  import type { PageProps } from './$types';
  import FileViewPage from '$lib/components/files/FileViewPage.svelte';


  let { data }: PageProps = $props();

</script>

<div class="flex w-full px-2 pb-10">
  <div class="w-full">
    <FileViewPage
      file={data.rawFile}
      splitPath={data.splitPath}
      registry={data.registryType}
      space={data.metadata.space}
      name={data.metadata.name}
      version={data.metadata.version}
    />
  </div>
</div>