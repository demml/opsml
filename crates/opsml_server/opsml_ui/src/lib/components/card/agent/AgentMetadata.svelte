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
    useCardContent = `from pyshipt_opsml import CardRegistry

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

<div class="grid grid-cols-1 gap-3 w-full h-auto">
  <!-- Header -->
  <div class="flex flex-row justify-between pb-2 mb-2 items-center border-b-2 border-black">
    <div class="flex flex-row items-center pt-2">
      <Info color="#8059b6"/>
      <header class="pl-2 text-primary-950 text-base font-bold">Agent Metadata</header>
    </div>
    <div>
      <CodeModal 
        code={useCardContent} 
        language="python"
        message="Paste the following code into your Python script to load the agent"
        display="Use this agent"
      />
    </div>
  </div>

  <!-- Core Metadata -->
  <div class="flex flex-col space-y-1 text-sm">
    <Pill key="Agent Name" value={agentSpec.name} textSize="text-sm"/>
    <Pill key="Version" value={agentSpec.version} textSize="text-sm"/>
    <Pill key="Created At" value={createdAt} textSize="text-sm"/>
    <Pill key="UID" value={uid} textSize="text-sm"/>
    <Pill key="Space" value={space} textSize="text-sm"/>
    <Pill key="Card Name" value={name} textSize="text-sm"/>
  </div>

  <!-- Description -->
  {#if agentSpec.description}
    <div class="flex flex-col space-y-2">
      <div class="flex flex-row items-center pb-1 border-b-2 border-black">
        <Info color="#8059b6"/>
        <header class="pl-2 text-primary-900 text-sm font-bold">Description</header>
      </div>
      <p class="text-sm text-gray-700 leading-relaxed">{agentSpec.description}</p>
    </div>
  {/if}

  <!-- Provider Info -->
  {#if agentSpec.provider}
    <div class="flex flex-col space-y-1">
      <div class="flex flex-row items-center pb-1 border-b-2 border-black">
        <Shield color="#8059b6"/>
        <header class="pl-2 text-primary-900 text-sm font-bold">Provider</header>
      </div>
      <Pill key="Organization" value={agentSpec.provider.organization} textSize="text-sm"/>
      
      {#if agentSpec.provider.url}
        <a 
          href={agentSpec.provider.url} 
          target="_blank" 
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1 text-sm text-primary-600 hover:text-primary-800 hover:underline"
        >
          <ExternalLink class="w-3 h-3" />
          {agentSpec.provider.url}
        </a>
      {/if}
    </div>
  {/if}

  <!-- Links -->
  {#if agentSpec.documentationUrl || agentSpec.iconUrl}
    <div class="flex flex-col space-y-2">
      <div class="flex flex-row items-center pb-1 border-b-2 border-black">
        <ExternalLink color="#8059b6"/>
        <header class="pl-2 text-primary-900 text-sm font-bold">Links</header>
      </div>
      <div class="flex flex-col gap-2">
        {#if agentSpec.documentationUrl}
          <a 
            href={agentSpec.documentationUrl} 
            target="_blank" 
            rel="noopener noreferrer"
            class="inline-flex items-center gap-2 px-3 py-2 bg-primary-100 hover:bg-primary-200 border-2 border-black rounded-lg text-sm font-bold transition-colors"
          >
            <ExternalLink class="w-4 h-4" />
            Documentation
          </a>
        {/if}
        {#if agentSpec.iconUrl}
          <div class="flex items-center gap-2">
            <span class="text-sm font-bold text-gray-700">Icon:</span>
            <img src={agentSpec.iconUrl} alt="Agent icon" class="w-8 h-8 rounded border-2 border-black" />
          </div>
        {/if}
      </div>
    </div>
  {/if}

  <!-- Input/Output Modes -->
  <div class="flex flex-col space-y-2">
    <div class="flex flex-row items-center pb-1 border-b-2 border-black">
      <Tags color="#8059b6"/>
      <header class="pl-2 text-primary-900 text-sm font-bold">Default Modes</header>
    </div>
    

    <div class="flex flex-wrap gap-3 space-y-2">
        {#if agentSpec.defaultInputModes.length > 0}
        <div class="space-y-1">
            <span class="text-xs font-bold text-gray-600 uppercase">Input Modes</span>
            <div class="flex flex-wrap gap-1">
            {#each agentSpec.defaultInputModes as mode}
                <span class="badge text-secondary-900 border-black border-1 shadow-small bg-secondary-100 text-xs">
                {mode}
                </span>
            {/each}
            </div>
        </div>
        {/if}

        {#if agentSpec.defaultOutputModes.length > 0}
        <div class="space-y-1">
            <span class="text-xs font-bold text-gray-600 uppercase">Output Modes</span>
            <div class="flex flex-wrap gap-1">
            {#each agentSpec.defaultOutputModes as mode}
                <span class="badge text-secondary-900 border-black border-1 shadow-small bg-secondary-100 text-xs">
                {mode}
                </span>
            {/each}
            </div>
        </div>
        {/if}
    </div>
  </div>
</div>
