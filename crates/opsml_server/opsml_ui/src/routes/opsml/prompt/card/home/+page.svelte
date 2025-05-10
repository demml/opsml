<script lang="ts">
  import { goto } from '$app/navigation';
  import type { PromptCard } from '$lib/components/card/card_interfaces/promptcard';
  import type { PageProps } from './$types';
  import CardReadMe from '$lib/components/card/CardReadMe.svelte';
  import NoReadme from '$lib/components/readme/NoReadme.svelte';
  import Metadata from '$lib/components/card/prompt/Metadata.svelte';


  let { data }: PageProps = $props();
  let metadata: PromptCard = data.metadata;

  function navigateToReadMe() {
      // navigate to readme
      goto(`/opsml/${data.registryPath}/card/readme?space=${metadata.space}&name=${metadata.name}&version=${metadata.version}`);
    }

</script>

<div class="flex-1 mx-auto w-11/12 flex justify-center px-4 pb-10">
  <div class="flex flex-wrap xl:flex-row pt-4 gap-4 w-full justify-center">

    {#if data.readme.exists}
      <div class="gap-1 flex flex-col rounded-base border-black border-3 shadow bg-surface-50 w-[1000px]">
        <CardReadMe
          name={metadata.name}
          space={metadata.space}
          registryPath={data.registryPath}
          version={metadata.version}
          readMe={data.readme}
        />
      </div>

     
    {:else}
      <div class="gap-1 flex flex-col rounded-base border-black border-3 shadow bg-primary-100 w-[600px] h-[200px]">
        <NoReadme
          name={metadata.name}
          space={metadata.space}
          registryPath={data.registryPath}
          version={metadata.version}
        />
      </div>
    {/if}

    
    <div class="bg-primary-200 p-4 flex flex-col rounded-base bg-surface-50 border-primary-800 border-3 shadow-primary min-w-112 max-h-[800px] overflow-y-auto self-start">
      <Metadata metadata={metadata} />
    </div>
  </div>
</div>
  


  