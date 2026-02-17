<script lang="ts">
  import FileTree from '$lib/components/files/FileTree.svelte'
  import type { PageProps } from './$types';
  import { page } from '$app/state';

  let { data }: PageProps = $props();


  </script>

  <div class="mx-auto w-9/12 px-4 py-4 max-h-[calc(100vh-140px)]">
    <div class="w-full">
      <FileTree
        files={data.fileTree.files}
        currentPath={page.url.pathname}
        previousPath={data.previousPath}
        space={data.metadata.space}
        name={data.metadata.name}
        version={data.metadata.version}
        isRoot={data.isRoot}
        registryType={data.registryType}
        />
    </div>
  </div>