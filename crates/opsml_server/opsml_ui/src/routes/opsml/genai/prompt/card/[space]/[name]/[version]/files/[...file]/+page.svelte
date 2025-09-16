<script lang="ts">
  import FileTree from '$lib/components/files/FileTree.svelte'
  import type { PageProps } from './$types';
  import { page } from '$app/state';

    let { data }: PageProps = $props();

 
  </script>
  
  <div class="flex-1 mx-auto w-9/12 pb-10 flex justify-center overflow-auto px-4">
    <div class="w-full pt-4">
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