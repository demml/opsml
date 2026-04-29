
<script lang="ts">
  import { onMount } from "svelte";
  import type { ExperimentCard } from "$lib/components/card/card_interfaces/experimentcard";
  import { Info, Diamond, Tags, HardDrive } from 'lucide-svelte';
  import CodeModal from "../CodeModal.svelte";
  import Pill from "$lib/components/utils/Pill.svelte";
  import LinkPill from "$lib/components/utils/LinkPill.svelte";
  import { formatBytes } from "$lib/components/files/utils";
  import { RegistryType } from "$lib/utils";
  import { type Parameter } from "$lib/components/card/card_interfaces/experimentcard";
  import ParameterModal from "./ParameterModal.svelte";

let {
    card,
    parameters
  } = $props<{
    card: ExperimentCard;
    parameters: Parameter[]
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

  <div class="flex flex-row justify-between pb-2 mb-1 items-center border-b-2 border-black">
    
    <div class="flex flex-row items-center gap-2">
      <div class="p-1.5 bg-primary-500 border-2 border-black rounded-base">
        <Info class="w-3.5 h-3.5 text-white" />
      </div>
      <header class="text-primary-950 text-sm font-black uppercase tracking-wide">Experiment Metadata</header>
    </div>

    <CodeModal 
      code={useCardContent} 
      language="python"
      message="Paste the following code into your Python script to load the card"
      display="Use this card"
    />
  </div>


  <div class="flex flex-col gap-1.5 text-sm">
    <Pill key="Created At" value={card.created_at} textSize="text-sm" />
    <Pill key="ID" value={card.uid} textSize="text-sm" />
    <Pill key="Space" value={card.space} textSize="text-sm" />
    <Pill key="Name" value={card.name} textSize="text-sm" />
    <Pill key="Version" value={card.version} textSize="text-sm" />
    <Pill key="OpsML Version" value={card.opsml_version} textSize="text-sm" />

  </div>

  {#if card.uids.datacard_uids || card.uids.modelcard_uids ||  card.uids.promptcard_uids ||  card.uids.experimentcard_uids}
    <div class="flex flex-col gap-2">
      <div class="flex flex-row items-center gap-2 pb-1 border-b-2 border-black">
        <div class="p-1.5 bg-tertiary-100 border-2 border-black rounded-base">
          <Diamond class="w-3.5 h-3.5 text-tertiary-950" fill="currentColor" />
        </div>
        <header class="text-primary-900 text-xs font-black uppercase tracking-wide">Linked Cards</header>
      </div>

      <div class="flex flex-wrap gap-1">
        {#if card.uids.datacard_uids}
          {#each card.uids.datacard_uids as datacard_uid (datacard_uid)}
            <LinkPill key="Data" uid={datacard_uid} registryType={RegistryType.Data} />
          {/each}
        {/if}

        {#if card.uids.experimentcard_uids}
          {#each card.uids.experimentcard_uids as experimentcard_uid (experimentcard_uid)}
            <LinkPill key="Experiment" uid={experimentcard_uid} registryType={RegistryType.Experiment} />
          {/each}
        {/if}

        {#if card.uids.modelcard_uids}
          {#each card.uids.modelcard_uids as modelcard_uid (modelcard_uid)}
            <LinkPill key="Model" uid={modelcard_uid} registryType={RegistryType.Model} />
          {/each}
        {/if}

        {#if card.uids.promptcard_uids}
          {#each card.uids.promptcard_uids as promptcard_uid (promptcard_uid)}
            <LinkPill key="Prompt" uid={promptcard_uid} registryType={RegistryType.Prompt} />
          {/each}
        {/if}
      </div>
    </div>
  {/if}

  {#if parameters.length > 0}
    <div class="flex flex-col gap-2">
      <div class="flex flex-row items-center gap-2 pb-1 border-b-2 border-black">
        <div class="p-1.5 bg-secondary-300 border-2 border-black rounded-base">
          <Tags class="w-3.5 h-3.5 text-black" />
        </div>
        <header class="text-primary-900 text-xs font-black uppercase tracking-wide">Parameters</header>
      </div>

      <div class="flex flex-wrap gap-2">
        <ParameterModal parameters={parameters} />
      </div>
    </div>
  {/if}

  {#if card.tags.length > 0}
    <div class="flex flex-col gap-2">
      <div class="flex flex-row items-center gap-2 pb-1 border-b-2 border-black">
        <div class="p-1.5 bg-tertiary-100 border-2 border-black rounded-base">
          <Tags class="w-3.5 h-3.5 text-tertiary-950" />
        </div>
        <header class="text-primary-900 text-xs font-black uppercase tracking-wide">Tags</header>
      </div>

      <div class="flex flex-wrap gap-1">
        {#each card.tags as tag (tag)}
          <span class="badge bg-primary-100 text-primary-900 border border-black shadow-small text-xs font-bold">
            {tag}
          </span>
        {/each}
      </div>
    </div>
  {/if}

  <div class="flex flex-col gap-2">
    <div class="flex flex-row items-center gap-2 pb-1 border-b-2 border-black">
      <div class="p-1.5 bg-primary-100 border-2 border-black rounded-base">
        <HardDrive class="w-3.5 h-3.5 text-primary-800" />
      </div>
      <header class="text-primary-900 text-xs font-black uppercase tracking-wide">Compute Environment</header>
    </div>

    <div class="flex flex-col gap-1.5 text-sm">
      <Pill key="CPU Count" value={card.compute_environment.cpu_count} textSize="text-sm" />
      <Pill key="Total Memory" value={formatBytes(card.compute_environment.total_memory)} textSize="text-sm" />
      <Pill key="Total Swap" value={formatBytes(card.compute_environment.total_swap)} textSize="text-sm" />
      <Pill key="System" value={card.compute_environment.system} textSize="text-sm" />
      <Pill key="OS Version" value={card.compute_environment.os_version} textSize="text-sm" />
      <Pill key="Hostname" value={card.compute_environment.hostname} textSize="text-sm" />
      <Pill key="Python" value={card.compute_environment.python_version} textSize="text-sm" />
    </div>
  </div>

  
</div>
