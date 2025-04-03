<script lang="ts">
  // version $props() in +page.svelte

  import { goto } from '$app/navigation';
  import type { ModelCard } from '$lib/components/card/card_interfaces/modelcard';
  import type { PageProps } from './$types';
  import CardReadMe from '$lib/components/card/CardReadMe.svelte';
  import Metadata from '$lib/components/card/model/Metadata.svelte';


  let { data }: PageProps = $props();
  let metadata: ModelCard = data.metadata;

  function navigateToReadMe() {
      // navigate to readme
      goto(`/opsml/${data.registryPath}/card/readme?repository=${metadata.repository}&name=${metadata.name}&version=${metadata.version}`);
    }

</script>


<div class="flex-1 mx-auto w-11/12 flex justify-center px-4 pb-10">
  <div class="flex flex-wrap xl:flex-row pt-4 gap-4 w-full justify-center" >

    {#if data.readme.exists}
      <div class="gap-1 flex flex-col rounded-base border-black border-3 shadow bg-surface-50 w-[1200px]">
        <CardReadMe
          name={metadata.name}
          repository={metadata.repository}
          registryPath={data.registryPath}
          version={metadata.version}
          readMe={data.readme}
        />
      </div>

     
    {:else}
    <div class="mx-auto gap-1 flex flex-col rounded-base border-black border-3 shadow bg-primary-100 w-1/3 h-1/4">
        <div class="flex flex-col items-center justify-center h-full gap-4">
          <div class="text-center text-xl font-bold text-black">No ReadMe found</div>
          <div>
            <button 
              class="mb-2 text-black bg-primary-500 rounded-lg shadow shadow-hover border-black border-2 px-4 w-38 h-10"
              onclick={navigateToReadMe}
            >
              add ReadMe
            </button>
          </div>
        </div>
      </div>
    {/if}


    
    <div class="bg-primary-200 p-4 flex flex-col rounded-base bg-surface-50 border-primary-800 border-3 shadow-primary min-w-112 max-h-[800px] overflow-y-auto self-start">
      <Metadata 
        metadata={metadata} 
        savedata={metadata.metadata.interface_metadata.save_metadata} 
        />
    </div>
  </div>
</div>
  


  