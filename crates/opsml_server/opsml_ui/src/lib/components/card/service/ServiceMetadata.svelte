
<script lang="ts">
  import { onMount } from "svelte";
  import type { ServiceCard, DeploymentConfig, ServiceConfig, ServiceMetadata } from "$lib/components/card/card_interfaces/servicecard";
  import { Info, Diamond, Tags, Rocket } from 'lucide-svelte';
  import CodeModal from "../CodeModal.svelte";
  import Pill from "$lib/components/utils/Pill.svelte";
  import LinkPill from "$lib/components/utils/LinkPill.svelte";
  import { RegistryType } from "$lib/utils";
  import { python } from "svelte-highlight/languages";

let {service} = $props<{service: ServiceCard;}>();

  let useCardContent = $state('');
  let deploymentConfig: DeploymentConfig | undefined = $state(service.deploy);
  let serviceConfig: ServiceConfig = $state(service.service_config);
  let metadata: ServiceMetadata | undefined = $state(service.metadata);


  onMount(() => {
 
    useCardContent = `from opsml import CardRegistry

# load the card
registry = CardRegistry('service')
service = registry.load_card(uid="${service.uid}")

# load the model
service.load()
`;
  })

</script>


<div class="grid grid-cols-1 gap-3 w-full h-auto">

  <div class="flex flex-row justify-between pb-2 mb-2 items-center border-b-2 border-black">
    
    <div class="flex flex-row items-center pt-2">
      <Info color="#8059b6"/>
      <header class="pl-2 text-primary-950 text-base font-bold">Metadata</header>
    </div>

    <div>
        <CodeModal 
          code={useCardContent} 
          language={python} 
          message="Paste the following code into your Python script to load the card"
          display="Use this card"
        />
    </div>
  </div>


  <div class="flex flex-col space-y-1 text-sm">

    <Pill key="Created At" value={service.created_at} textSize="text-sm"/>
    <Pill key="ID" value={service.uid} textSize="text-sm"/>
    <Pill key="Space" value={service.space} textSize="text-sm"/>
    <Pill key="Name" value={service.name} textSize="text-sm"/>
    <Pill key="Version" value={service.opsml_version} textSize="text-sm"/>

  </div>

  {#if service.experimentcard_uid }
    <div class="flex flex-row items-center pb-1 border-b-2 border-black">
      <Diamond color="#8059b6" fill="#8059b6"/>
      <header class="pl-2 text-primary-900 text-sm font-bold">Cards</header>
    </div>

    <div class="flex flex-wrap space-y-1 gap-1">
      {#if service.experimentcard_uid}
        <LinkPill key="Experiment" uid={service.experimentcard_uid} registryType={RegistryType.Experiment} />
      {/if}
    </div>
  {/if}

  {#if metadata && metadata.tags.length > 0}
    <div class="flex flex-col space-y-1 gap-1">
      <div class="flex flex-row items-center pb-1 border-b-2 border-black">
        <Tags color="#8059b6" />
        <header class="pl-2 text-primary-900 text-sm font-bold">Tags</header>
      </div>
    </div>

    <div class="flex flex-wrap gap-1">
      {#each metadata.tags as tag}
        <div class="inline-flex items-center overflow-hidden rounded-lg bg-primary-100 border border-primary-800 text-sm w-fit px-2 text-primary-900">
          {tag}
        </div>
      {/each}
    </div>
  {/if}

  {#if deploymentConfig}
    <div class="flex flex-row items-center pb-1 border-b-2 border-black">
      <Rocket color="#8059b6" />
      <header class="pl-2 text-primary-900 text-sm font-bold">Deployment Configuration</header>
    </div>

    <div class="flex flex-col space-y-1 text-sm">
    <Pill key="Environment" value={deploymentConfig.environment} textSize="text-sm" />
    {#if deploymentConfig.location}
      <Pill key="Location" value={deploymentConfig.location} textSize="text-sm" />
    {/if}
    
  </div>
  {/if}
  
</div>