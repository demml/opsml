<script lang="ts">
  // version $props() in +page.svelte

  import HomePage from '$lib/components/model/ReadMe.svelte';
  import type { ModelCard } from '$lib/components/card/card_interfaces/modelcard';
  import type { PageProps } from './$types';
  import { onMount } from 'svelte';
  import ReadMe from '$lib/components/model/ReadMe.svelte';
  import Metadata from '$lib/components/model/Metadata.svelte';

  let { data }: PageProps = $props();
  let metadata: ModelCard = data.metadata;

</script>


<div class="mx-auto w-11/12 pb-10 flex justify-center min-h-screen">
  <div class="grid grid-cols-1 md:grid-cols-6 gap-4 w-full pt-4">

    <div class="col-span-1 md:col-span-4 gap-1 flex flex-col rounded-base border-black border-3 shadow bg-surface-50 w-full">
      <ReadMe
        name={metadata.name}
        repository={metadata.repository}
        registry={data.registry}
        version={metadata.version}
        content={data.content}
      />
    </div>

    <div class="col-span-1 md:col-span-2 bg-primary-200 p-4 flex flex-col rounded-base bg-surface-50 border-primary-800 border-3 shadow-primary h-[50%] min-h-fit">
      <Metadata metadata={metadata} savedata={metadata.metadata.interface_metadata.save_metadata} />
    </div>
  </div>
</div>
  


  