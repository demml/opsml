
<script lang="ts">
  import { onMount } from "svelte";
  import type { ExperimentCard } from "$lib/components/card/card_interfaces/experimentcard";
  import { Info, Diamond, Tags } from 'lucide-svelte';
  import CodeModal from "../CodeModal.svelte";
  import Pill from "$lib/components/utils/Pill.svelte";
  import LinkPill from "$lib/components/utils/LinkPill.svelte";
  import { formatBytes } from "$lib/components/files/utils";
  import { HardDrive } from 'lucide-svelte';
  import { RegistryType } from "$lib/utils";

let {
    card,
  } = $props<{
    card: ExperimentCard;
  }>();


  let useCardContent = $state('');

  onMount(() => {
    useCardContent = `from opsml import CardRegistry

# load the card
registry = CardRegistry('experiment')
experimentcard = registry.load_card(uid="${card.uid}")
`;
  })

</script>


<div class="grid grid-cols-1 gap-4 w-full h-auto">

  <div class="flex flex-row justify-between pb-2 mb-2 items-center border-b-2 border-black">
    
    <div class="flex flex-row items-center pt-2">
      <Info color="#8059b6"/>
      <header class="pl-2 text-primary-950 text-2xl font-bold">Metadata</header>
    </div>

    <div>
        <CodeModal code={useCardContent} language="python" />
    </div>
  </div>


  <div class="flex flex-col space-y-1 text-base">
    <Pill key="Created At" value={card.created_at} textSize="text-base" />
    <Pill key="ID" value={card.uid} textSize="text-base" />
    <Pill key="space" value={card.space} textSize="text-base" />
    <Pill key="Name" value={card.name} textSize="text-base" />
    <Pill key="Version" value={card.version} textSize="text-base" />
    <Pill key="OpsML Version" value={card.opsml_version} textSize="text-base" />

  </div>

  {#if card.uids.datacard_uids || card.uids.modelcard_uids ||  card.uids.promptcard_uids ||  card.uids.experimentcard_uids}
    <div class="flex flex-row items-center mb-1 border-b-2 border-black">
      <Diamond color="#8059b6" fill="#8059b6"/>
      <header class="pl-2 text-primary-900 text-lg font-bold">Cards</header>
    </div>

    <div class="flex flex-wrap space-y-1 gap-1">

      {#if card.uids.datacard_uids}
        {#each card.uids.datacard_uids as datacard_uid}
          <LinkPill key="Data" value={datacard_uid} registryType={RegistryType.Data} />
        {/each}
      {/if}

      {#if card.uids.experimentcard_uids}
        {#each card.uids.experimentcard_uids as experimentcard_uid}
          <LinkPill key="Experiment" value={experimentcard_uid} registryType={RegistryType.Experiment} />
        {/each}
      {/if}

      {#if card.uids.modelcard_uids}
        {#each card.uids.modelcard_uids as modelcard_uid}
          <LinkPill key="Model" value={modelcard_uid} registryType={RegistryType.Model} />
        {/each}
      {/if}

      {#if card.uids.promptcard_uids}
        {#each card.uids.promptcard_uids as promptcard_uid}
          <LinkPill key="Prompt" value={promptcard_uid} registryType={RegistryType.Prompt} />
        {/each}
      {/if}
    </div>
  {/if}

  {#if card.tags.length > 0}
    <div class="flex flex-col space-y-1 gap-1">
      <div class="flex flex-row items-center mb-1 border-b-2 border-black">
        <Tags color="#8059b6" />
        <header class="pl-2 text-primary-900 text-lg font-bold">Tags</header>
      </div>
    </div>

    <div class="flex flex-wrap gap-1">
      {#each card.tags as tag}
        <div class="inline-flex items-center overflow-hidden rounded-lg bg-primary-100 border border-primary-800 text-sm w-fit px-2 text-primary-900">
          {tag}
        </div>
      {/each}
    </div>
  {/if}

  <div class="flex flex-row items-center mb-1 border-b-2 border-black">
    <HardDrive color="#8059b6" />
    <header class="pl-2 text-primary-900 text-lg font-bold">Compute Environment</header>
  </div>

  <div class="flex flex-col space-y-1 text-base">
    <Pill key="CPU Count" value={card.compute_environment.cpu_count} textSize="text-base" />
    <Pill key="Total Memory" value={formatBytes(card.compute_environment.total_memory)} textSize="text-base" />
    <Pill key="Total Swap" value={formatBytes(card.compute_environment.total_swap)} textSize="text-base" />
    <Pill key="System" value={card.compute_environment.system} textSize="text-base" />
    <Pill key="OS Version" value={card.compute_environment.os_version} textSize="text-base" />
    <Pill key="Hostname" value={card.compute_environment.hostname} textSize="text-base" />
    <Pill key="Python" value={card.compute_environment.python_version} textSize="text-base" />
  </div>

  
</div>