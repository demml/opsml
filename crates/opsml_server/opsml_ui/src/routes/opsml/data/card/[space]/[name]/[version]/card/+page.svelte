<script lang="ts">
  import type { DataCard } from '$lib/components/card/card_interfaces/datacard';
  import type { PageProps } from './$types';
  import CardReadMe from '$lib/components/card/CardReadMe.svelte';
  import NoReadme from '$lib/components/readme/NoReadme.svelte';
  import Metadata from '$lib/components/card/data/Metadata.svelte';


  let { data }: PageProps = $props();
  let card: DataCard = data.metadata;

</script>

<div class="flex-1 mx-auto w-11/12 flex justify-center px-4 pb-10">
  <div class="flex flex-wrap pt-4 gap-4 w-full justify-center">

    {#if data.readme.exists}
      <div class="gap-1 flex flex-col rounded-base border-black border-3 shadow bg-surface-50 w-[800px]">
        <CardReadMe
          name={card.name}
          space={card.space}
          registryPath={data.registryPath}
          version={card.version}
          readMe={data.readme}
        />
      </div>

     
    {:else}
      <div class="gap-1 flex flex-col rounded-base border-black border-3 shadow bg-primary-100 w-[500px] h-[200px]">
        <NoReadme
          name={card.name}
          space={card.space}
          registryPath={data.registryPath}
          version={card.version}
        />
      </div>
    {/if}

    
    <div class="bg-primary-200 p-4 flex-1 flex-col rounded-base bg-surface-50 border-primary-800 border-3 shadow-primary max-h-[800px] overflow-y-auto self-start min-w-0 max-w-[300px] md:min-w-[26rem] md:max-w-[32rem]">
      <Metadata 
        card={card} 
        interfaceMetadata={card.metadata.interface_metadata}
        saveMetadata={card.metadata.interface_metadata.save_metadata}
        />
    </div>
  </div>
</div>
  


  