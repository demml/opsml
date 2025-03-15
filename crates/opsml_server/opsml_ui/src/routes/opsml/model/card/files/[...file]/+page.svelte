<script lang="ts">
  import FileTree from '$lib/components/files/FileTree.svelte'
  import type { PageProps } from './$types';
  import { page } from '$app/state';

    let { data }: PageProps = $props();

 
  </script>
  
  <div class="mx-auto w-9/12 pb-10 flex justify-center min-h-screen">
    <div class="w-full pt-4">
      <FileTree 
        files={data.fileTree.files} 
        currentPath={page.url.pathname} 
        previousPath={data.previousPath} 
        repository={data.metadata.repository}
        name={data.metadata.name}
        version={data.metadata.version}
        isRoot={data.isRoot}
        registryPath={data.registryPath}
        />
    </div>  
  </div>