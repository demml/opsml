
<script lang="ts">
  import { onMount } from "svelte";
  import type { PromptCard } from "$lib/components/card/card_interfaces/promptcard";
  import { Info, Diamond, Tags, Settings, MessageSquareText, ListChecks } from 'lucide-svelte';
  import CodeModal from "../CodeModal.svelte";
  import Pill from "$lib/components/utils/Pill.svelte";
  import PromptModal from "./common/PromptModal.svelte";
  import LinkPill from "$lib/components/utils/LinkPill.svelte";
  import { RegistryType } from "$lib/utils";
  import ResponseSchemaModal from "./ResponseSchemaModal.svelte";
  import EvalTasksModal from "./common/EvalTasksModal.svelte";

  let { card } = $props<{ card: PromptCard }>();

  let useCardContent = $state('');

  onMount(() => {
    useCardContent = `from opsml import CardRegistry

# load the card
registry = CardRegistry('prompt')
card = registry.load_card(uid="${card.uid}")
`;
  });
</script>


<div class="grid grid-cols-1 gap-4 w-full h-auto">

  <!-- Header -->
  <div class="flex flex-row justify-between pb-2 mb-1 items-center border-b-2 border-black">
    <div class="flex flex-row items-center gap-2">
      <div class="p-1.5 bg-primary-500 border-2 border-black rounded-base">
        <Info class="w-3.5 h-3.5 text-white" />
      </div>
      <header class="text-primary-950 text-sm font-black uppercase tracking-wide">Prompt Metadata</header>
    </div>
    <CodeModal
      code={useCardContent}
      language="python"
      message="Paste the following code into your Python script to load the card"
      display="Use this card"
    />
  </div>

  <!-- Core Metadata -->
  <div class="flex flex-col gap-1.5 text-sm">
    <Pill key="Created At" value={card.created_at} textSize="text-sm"/>
    <Pill key="ID" value={card.uid} textSize="text-sm"/>
    <Pill key="Space" value={card.space} textSize="text-sm"/>
    <Pill key="Name" value={card.name} textSize="text-sm"/>
    <Pill key="Version" value={card.version} textSize="text-sm"/>
    <Pill key="OpsML Version" value={card.opsml_version} textSize="text-sm"/>
  </div>

  <!-- Associated Cards -->
  {#if card.metadata.experimentcard_uid || card.metadata.auditcard_uid}
    <div class="flex flex-col gap-2">
      <div class="flex flex-row items-center gap-2 pb-1 border-b-2 border-black">
        <div class="p-1.5 bg-tertiary-100 border-2 border-black rounded-base">
          <Diamond class="w-3.5 h-3.5 text-tertiary-950" fill="currentColor" />
        </div>
        <header class="text-primary-900 text-xs font-black uppercase tracking-wide">Linked Cards</header>
      </div>
      <div class="flex flex-wrap gap-1">
        {#if card.metadata.experimentcard_uid}
          <LinkPill key="Experiment" uid={card.metadata.experimentcard_uid} registryType={RegistryType.Experiment} />
        {/if}
      </div>
    </div>
  {/if}

  <!-- Prompts -->
  <div class="flex flex-col gap-2">
    <div class="flex flex-row items-center gap-2 pb-1 border-b-2 border-black">
      <div class="p-1.5 bg-secondary-300 border-2 border-black rounded-base">
        <MessageSquareText class="w-3.5 h-3.5 text-black" />
      </div>
      <header class="text-primary-900 text-xs font-black uppercase tracking-wide">Prompts</header>
    </div>
    <div class="flex flex-wrap gap-2">
      <PromptModal prompt={card.prompt} />
      {#if card.prompt.response_json_schema}
        <ResponseSchemaModal prompt={card.prompt} />
      {/if}
    </div>
  </div>

  <!-- Model Settings -->
  <div class="flex flex-col gap-2">
    <div class="flex flex-row items-center gap-2 pb-1 border-b-2 border-black">
      <div class="p-1.5 bg-primary-100 border-2 border-black rounded-base">
        <Settings class="w-3.5 h-3.5 text-primary-800" />
      </div>
      <header class="text-primary-900 text-xs font-black uppercase tracking-wide">Model Settings</header>
    </div>
    <div class="flex flex-wrap gap-1.5">
      <Pill key="Model" value={card.prompt.model} textSize="text-sm"/>
      <Pill key="Provider" value={card.prompt.provider} textSize="text-sm"/>
    </div>
  </div>

  <!-- Evaluation Profile -->
  {#if card.eval_profile}
    <div class="flex flex-col gap-2">
      <div class="flex flex-row items-center gap-2 pb-1 border-b-2 border-black">
        <div class="p-1.5 bg-secondary-300 border-2 border-black rounded-base">
          <ListChecks class="w-3.5 h-3.5 text-black" />
        </div>
        <header class="text-primary-900 text-xs font-black uppercase tracking-wide">Evaluation Profile</header>
      </div>
      <div class="flex flex-wrap gap-2">
        <EvalTasksModal evalProfile={card.eval_profile} />
      </div>
    </div>
  {/if}

  <!-- Tags -->
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

  <!-- Parameters -->
  {#if card.prompt.parameters}
    <div class="flex flex-col gap-2">
      <div class="flex flex-row items-center gap-2 pb-1 border-b-2 border-black">
        <div class="p-1.5 bg-secondary-300 border-2 border-black rounded-base">
          <Tags class="w-3.5 h-3.5 text-black" />
        </div>
        <header class="text-primary-900 text-xs font-black uppercase tracking-wide">Parameters</header>
      </div>
      <div class="flex flex-wrap gap-1">
        {#each card.prompt.parameters as param (param)}
          <span class="badge bg-secondary-100 text-secondary-950 border border-black shadow-small text-xs font-bold">
            {param}
          </span>
        {/each}
      </div>
    </div>
  {/if}

</div>
