<script lang="ts">
  import { onMount } from "svelte";
  import type { AgentSpec } from "./types";
  import { Info, Tags, Shield, ExternalLink } from 'lucide-svelte';
  import CodeModal from "../CodeModal.svelte";
  import Pill from "$lib/components/utils/Pill.svelte";

  let { agentSpec, uid, createdAt, space, name, version } = $props<{
    agentSpec: AgentSpec;
    uid: string;
    createdAt: string;
    space: string;
    name: string;
    version: string;
  }>();

  let useCardContent = $state('');

  onMount(() => {
    useCardContent = `from opsml import CardRegistry

# load the agent service card
registry = CardRegistry('agent')
agent = registry.load_card(uid="${uid}")

# access agent spec
spec = agent.service_config.agent
print(f"Agent: {spec.name}")
print(f"Version: {spec.version}")
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
      <header class="text-primary-950 text-sm font-black uppercase tracking-wide">Agent Metadata</header>
    </div>
    <CodeModal
      code={useCardContent}
      language="python"
      message="Paste the following code into your Python script to load the agent"
      display="Use this agent"
    />
  </div>

  <!-- Core Metadata -->
  <div class="flex flex-col gap-1.5 text-sm">
    <Pill key="Agent Name" value={agentSpec.name} textSize="text-sm"/>
    <Pill key="Version" value={agentSpec.version} textSize="text-sm"/>
    <Pill key="Created At" value={createdAt} textSize="text-sm"/>
    <Pill key="UID" value={uid} textSize="text-sm"/>
    <Pill key="Space" value={space} textSize="text-sm"/>
    <Pill key="Card Name" value={name} textSize="text-sm"/>
  </div>

  <!-- Description -->
  {#if agentSpec.description}
    <div class="flex flex-col gap-2">
      <div class="flex flex-row items-center gap-2 pb-1 border-b-2 border-black">
        <Info class="w-3.5 h-3.5" color="var(--color-primary-500)" />
        <header class="text-primary-900 text-xs font-black uppercase tracking-wide">Description</header>
      </div>
      <p class="text-sm text-black/70 leading-relaxed">{agentSpec.description}</p>
    </div>
  {/if}

  <!-- Provider Info -->
  {#if agentSpec.provider}
    <div class="flex flex-col gap-2">
      <div class="flex flex-row items-center gap-2 pb-1 border-b-2 border-black">
        <Shield class="w-3.5 h-3.5" color="var(--color-primary-500)" />
        <header class="text-primary-900 text-xs font-black uppercase tracking-wide">Provider</header>
      </div>
      <Pill key="Organization" value={agentSpec.provider.organization} textSize="text-sm"/>
      {#if agentSpec.provider.url}
        <a
          href={agentSpec.provider.url}
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1.5 px-3 py-2 bg-primary-100 hover:bg-primary-200 border-2 border-black shadow-small shadow-hover-small rounded-base text-xs font-bold transition-all duration-100"
        >
          <ExternalLink class="w-3.5 h-3.5" />
          {agentSpec.provider.url}
        </a>
      {/if}
    </div>
  {/if}

  <!-- Links -->
  {#if agentSpec.documentationUrl || agentSpec.iconUrl}
    <div class="flex flex-col gap-2">
      <div class="flex flex-row items-center gap-2 pb-1 border-b-2 border-black">
        <ExternalLink class="w-3.5 h-3.5" color="var(--color-primary-500)" />
        <header class="text-primary-900 text-xs font-black uppercase tracking-wide">Links</header>
      </div>
      <div class="flex flex-col gap-2">
        {#if agentSpec.documentationUrl}
          <a
            href={agentSpec.documentationUrl}
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-2 px-3 py-2 bg-primary-100 hover:bg-primary-200 border-2 border-black shadow-small shadow-hover-small rounded-base text-sm font-bold transition-all duration-100"
          >
            <ExternalLink class="w-4 h-4" />
            Documentation
          </a>
        {/if}
        {#if agentSpec.iconUrl}
          <div class="flex items-center gap-2">
            <span class="text-xs font-black text-primary-700 uppercase tracking-wide">Icon</span>
            <img src={agentSpec.iconUrl} alt="Agent icon" class="w-8 h-8 rounded-base border-2 border-black" />
          </div>
        {/if}
      </div>
    </div>
  {/if}

  <!-- Input/Output Modes -->
  <div class="flex flex-col gap-2">
    <div class="flex flex-row items-center gap-2 pb-1 border-b-2 border-black">
      <Tags class="w-3.5 h-3.5" color="var(--color-primary-500)" />
      <header class="text-primary-900 text-xs font-black uppercase tracking-wide">Default Modes</header>
    </div>
    <div class="flex flex-wrap gap-4">
      {#if agentSpec.defaultInputModes.length > 0}
        <div class="space-y-1">
          <span class="text-xs font-black text-primary-700 uppercase tracking-wide">Input</span>
          <div class="flex flex-wrap gap-1">
            {#each agentSpec.defaultInputModes as mode}
              <span class="badge text-black border-black border shadow-small bg-secondary-100 text-xs font-bold">{mode}</span>
            {/each}
          </div>
        </div>
      {/if}
      {#if agentSpec.defaultOutputModes.length > 0}
        <div class="space-y-1">
          <span class="text-xs font-black text-primary-700 uppercase tracking-wide">Output</span>
          <div class="flex flex-wrap gap-1">
            {#each agentSpec.defaultOutputModes as mode}
              <span class="badge text-black border-black border shadow-small bg-secondary-100 Text-xs font-bold">{mode}</span>
            {/each}
          </div>
        </div>
      {/if}
    </div>
  </div>

</div>
