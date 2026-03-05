<script lang="ts">
  import FileExplorer from '$lib/components/files/FileExplorer.svelte';
  import type { PageProps } from './$types';

  let { data }: PageProps = $props();
</script>

<div class="mx-auto px-4 w-full">
  <FileExplorer
    initialTree={data.fileTree.files}
    rawFile={data.rawFile}
    viewPath={data.viewPath}
    basePath={data.basePath}
    uid={data.metadata.uid}
    registryType={data.registryType}
    space={data.metadata.space}
    name={data.metadata.name}
    version={data.metadata.version}
  />
</div>
