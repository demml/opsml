<script lang="ts">

  import type { ServiceCard } from '$lib/components/card/card_interfaces/servicecard';
  import ServiceMetadata from '$lib/components/card/service/ServiceMetadata.svelte';
  import { Table } from 'lucide-svelte';
  import CardButton from '$lib/components/card/service/CardButton.svelte';
  import { getRegistryFromString, RegistryType } from '$lib/utils';
  import DeploymentConfig from '$lib/components/card/service/DeploymentConfig.svelte';
  let badgeColor = "#40328b";
  let iconColor = "#40328b";

  let { data } = $props();
  let service: ServiceCard = data.metadata;
  let deploymentConfig = service.deploy;

</script>


<div class="flex-1 flex-col mx-auto w-11/12 justify-center px-4 pb-10">

  <div class="flex flex-wrap pt-4 gap-4 w-full">

    <div class="bg-primary-200 p-4 flex-1 flex-col rounded-base bg-surface-50 border-primary-800 border-3 shadow-primary max-h-[800px] overflow-y-auto self-start min-w-[26rem] max-w-[300px] md:min-w-[26rem] md:max-w-[32rem]">
        <ServiceMetadata service={service}/>
    </div>

    {#if service.cards && service.cards.cards.length > 0}
      <div class="flex-1 flex-col rounded-base border-primary-500 border-2 shadow-primary bg-surface-50 pb-4 px-4">
        <div class="flex flex-row items-center gap-2 py-4">
          <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
            <Table color={iconColor} />
          </div>
          <span class="font-bold text-primary-800">Card List</span>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {#each service.cards.cards as card}
              <CardButton
                iconColor={iconColor} 
                badgeColor={badgeColor}
                name={card.name}
                space={card.space}
                version={card.version}
                registry={getRegistryFromString(card.registry_type) || RegistryType.Model}
                alias={card.alias}
              />
            {/each}
        </div>
      </div>
    {/if}
  </div>

  {#if deploymentConfig && deploymentConfig.length > 0}
    <div class="flex flex-wrap pt-4 gap-4 w-full">
      {#each deploymentConfig as config}
        <div class="bg-primary-200 p-4 flex-1 flex-col rounded-base bg-surface-50 border-primary-800 border-3 shadow-primary max-h-[800px] overflow-y-auto self-start min-w-[26rem] max-w-[300px] md:min-w-[26rem] md:max-w-[32rem]">
          <DeploymentConfig config={config}/>
        </div>
      {/each}
    </div>
  {/if}

</div>