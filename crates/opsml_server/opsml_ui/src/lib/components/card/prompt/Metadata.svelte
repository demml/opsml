
<script lang="ts">
  import { onMount } from "svelte";
  import type { PromptCard, ModelSettings } from "$lib/components/card/card_interfaces/promptcard";
  import { Info, Diamond, Tags } from 'lucide-svelte';
  import CodeModal from "../CodeModal.svelte";
  import Pill from "$lib/components/utils/Pill.svelte";
  import { Braces, CheckCheck, MessageSquareText, Settings } from 'lucide-svelte';
  import PromptModal from "./PromptModal.svelte";
  import ExtraModelSettings from "./ExtraModelSettings.svelte";


  let {
      metadata,
      modelSettings,
    } = $props<{
      metadata: PromptCard;
      modelSettings: ModelSettings;
    }>();


    let useCardContent = $state('');

    onMount(() => {
      useCardContent = `from opsml import CardRegistry

# load the card
registry = CardRegistry('prompt')
datacard = registry.load_card(uid="${metadata.uid}")
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
    <Pill key="Created At" value={metadata.created_at} />
    <Pill key="ID" value={metadata.uid} />
    <Pill key="space" value={metadata.space} />
    <Pill key="Name" value={metadata.name} />
    <Pill key="Version" value={metadata.version} />
    <Pill key="OpsML Version" value={metadata.opsml_version} />

  </div>

  <div class="flex flex-col space-y-1 gap-1">
    <div class="flex flex-row items-center mb-1 border-b-2 border-black">
      <MessageSquareText color="#8059b6" />
      <header class="pl-2 text-primary-900 text-lg font-bold">Prompts</header>
    </div>
  </div>

  <div class="flex flex-wrap gap-1">
    <PromptModal prompt={metadata.prompt}/>
  </div>


  <div class="flex flex-col space-y-1 gap-1">
    <div class="flex flex-row items-center mb-1 border-b-2 border-black">
      <Settings color="#8059b6" />
      <header class="pl-2 text-primary-900 text-lg font-bold">Model Settings</header>
    </div>
  </div>

  <div class="flex flex-wrap gap-1">

    <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit text-sm">
      <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Model</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
        {modelSettings.model}
      </div>
    </div>

    <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit text-sm">
      <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Provider</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
        {modelSettings.provider}
      </div>
    </div>

    {#if modelSettings.maxTokens}
      <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit text-sm">
        <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Max Tokens</div> 
        <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
          {modelSettings.max_tokens}
        </div>
      </div>
    {/if}

    {#if modelSettings.temperature}
      <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit text-sm">
        <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Temperature</div> 
        <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
          {modelSettings.temperature}
        </div>
      </div>
    {/if}

    {#if modelSettings.top_p}
      <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit text-sm">
        <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Top P</div> 
        <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
          {modelSettings.top_p}
        </div>
      </div>
    {/if}

    {#if modelSettings.frequency_penalty}
      <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit text-sm">
        <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Frequency Penalty</div> 
        <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
          {modelSettings.frequency_penalty}
        </div>
      </div>
    {/if}

    {#if modelSettings.presence_penalty}
      <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit text-sm">
        <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Presence Penalty</div> 
        <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
          {modelSettings.presence_penalty}
        </div>
      </div>
    {/if}

    {#if modelSettings.timeout}
      <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit text-sm">
        <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Timeout</div> 
        <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
          {modelSettings.timeout}
        </div>
      </div>
    {/if}

    {#if modelSettings.parallel_tool_calls}
      <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit text-sm">
        <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Parallel Tool Calls</div> 
        <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
          {modelSettings.parallel_tool_calls}
        </div>
      </div>
    {/if}

    {#if modelSettings.seed}
      <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit text-sm">
        <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Seed</div> 
        <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
          {modelSettings.seed}
        </div>
      </div>
    {/if}

    {#if modelSettings.logit_bias || 
      modelSettings.stop_sequences?.length > 0 || 
      modelSettings.extra_body}
      <ExtraModelSettings settings={modelSettings}/>
    {/if}

  </div>

  {#if metadata.tags.length > 0}
    <div class="flex flex-col space-y-1 gap-1">
      <div class="flex flex-row items-center mb-1 border-b-2 border-black">
        <Tags color="#8059b6" />
        <header class="pl-2 text-primary-900 text-lg font-bold">Tags</header>
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

  



</div>