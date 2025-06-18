<script lang="ts">
   import type { PageProps } from './$types';
   import ReadMe from '$lib/components/readme/Readme.svelte';


  let { data }: PageProps = $props();


</script>

<div class="flex-1 mx-auto w-7/12 pb-10 flex justify-center overflow-auto px-4">
  <div class="grid grid-cols-1 gap-4 w-full pt-4">
    <div class="col-span-1 md:col-span-4 gap-1 flex flex-col rounded-base border-black border-3 shadow bg-surface-50 w-full">
      <ReadMe
        name={data.metadata.name}
        space={data.metadata.space}
        version={data.metadata.version}
        registry={data.registry}
        registryPath={data.registryPath}
        readme_content={data.content}
      />
    </div>
  </div>
</div>
