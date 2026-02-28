<!--
  AgentEvalDashboard.svelte
  ─────────────────────────
  Main evaluation dashboard for an agent card. Shows a high-level overview
  of all associated prompt evaluations, then an expandable panel for each
  prompt card with its full GenAI evaluation dashboard.
-->
<script lang="ts">
  import type { AgentPromptEvalData } from './types';
  import AgentEvalOverview from './AgentEvalOverview.svelte';
  import AgentPromptEvalPanel from './AgentPromptEvalPanel.svelte';
  import { Bot } from 'lucide-svelte';

  interface Props {
    agentName: string;
    agentVersion: string;
    agentPromptEvals: AgentPromptEvalData[];
  }

  let { agentName, agentVersion, agentPromptEvals }: Props = $props();
</script>

<div class="mx-auto w-full px-4 sm:px-6 lg:px-8 pb-12 space-y-6">

  <!-- Agent identity banner -->
  <div class="rounded-base border-2 border-black bg-primary-50 shadow-small p-4 flex items-center gap-3">
    <div class="p-2 bg-primary-500 border-2 border-black rounded-base shadow-small flex-shrink-0">
      <Bot class="w-5 h-5 text-white" />
    </div>
    <div>
      <p class="text-xs font-black uppercase tracking-wider text-slate-500">Agent</p>
      <p class="font-black text-black">
        {agentName}
        <span class="ml-2 badge bg-surface-50 text-primary-800 border border-black text-xs font-bold px-2 py-0.5 rounded-full">
          v{agentVersion}
        </span>
      </p>
    </div>
    <div class="ml-auto text-right">
      <p class="text-xs font-black uppercase tracking-wider text-slate-500">Evaluating</p>
      <p class="font-black text-primary-800">
        {agentPromptEvals.length} Prompt{agentPromptEvals.length !== 1 ? 's' : ''}
      </p>
    </div>
  </div>

  <!-- High-level aggregate stats -->
  <div>
    <h2 class="text-xs font-black uppercase tracking-wider text-slate-500 mb-3">Overview</h2>
    <AgentEvalOverview {agentPromptEvals} />
  </div>

  <!-- Per-prompt evaluation panels -->
  <div class="space-y-4">
    <h2 class="text-xs font-black uppercase tracking-wider text-slate-500">
      Prompt Evaluations
    </h2>

    {#each agentPromptEvals as evalData, index (evalData.promptCard.uid)}
      <AgentPromptEvalPanel
        promptCard={evalData.promptCard}
        monitoringData={evalData.monitoringData}
        expanded={index === 0}
      />
    {/each}
  </div>
</div>
