<!--
  AgentPromptEvalPanel.svelte
  ───────────────────────────
  Reusable panel that shows the full GenAI evaluation dashboard for a single
  prompt card associated with an agent. This mirrors the prompt evaluation page
  but is designed to be embedded inside the agent evaluation route.
-->
<script lang="ts">

  import type { PromptCard } from '$lib/components/card/card_interfaces/promptcard';
  import type { GenAIMonitoringPageData } from '$lib/components/scouter/dashboard/utils';
  import { refreshGenAIMonitoringData } from '$lib/components/scouter/dashboard/utils';
  import type { RecordCursor } from '$lib/components/scouter/types';
  import { getRegistryPath, RegistryType } from '$lib/utils';
  import { Loader2, MessageSquareText, ExternalLink, AlertCircle } from 'lucide-svelte';
  import GenAIDashboard from '$lib/components/scouter/genai/dashboard/GenAIDashboard.svelte';
  import GenAITaskAccordion from '$lib/components/scouter/genai/task/GenAITaskAccordion.svelte';
  import { timeRangeState } from '$lib/components/utils/timeState.svelte';

  interface Props {
    promptCard: PromptCard;
    monitoringData: GenAIMonitoringPageData;
    /** Whether the panel starts expanded (default: true for first panel, false for rest) */
    expanded?: boolean;
  }

  let { promptCard, monitoringData: initialData, expanded = true }: Props = $props();

  let monitoringData = $state<GenAIMonitoringPageData>(initialData);
  let isRefreshing = $state(false);
  let isExpanded = $state(expanded);

  // Prompt card link to its own evaluation page
  let promptEvalPath = $derived(
    `/opsml/${getRegistryPath(RegistryType.Prompt)}/card/${promptCard.space}/${promptCard.name}/${promptCard.version}/evaluation`
  );

  // React to global time range changes
  $effect(() => {
    const newRange = timeRangeState.selectedTimeRange;
    if (newRange && monitoringData.status === 'success') {
      const currentRange = monitoringData.selectedTimeRange;
      if (
        currentRange.startTime !== newRange.startTime ||
        currentRange.endTime !== newRange.endTime
      ) {
        monitoringData.selectedTimeRange = newRange;
        performRefresh();
      }
    }
  });

  async function performRefresh(
    rCursor?: { cursor: RecordCursor; direction: string },
    wCursor?: { cursor: RecordCursor; direction: string }
  ) {
    if (monitoringData.status !== 'success') return;
    isRefreshing = true;
    try {
      await refreshGenAIMonitoringData(fetch, monitoringData, {
        recordCursor: rCursor,
        workflowCursor: wCursor,
      });
    } catch (e) {
      console.error(`[AgentPromptEvalPanel] Refresh failed for ${promptCard.name}:`, e);
    } finally {
      isRefreshing = false;
    }
  }

  async function handleRecordPageChange(cursor: RecordCursor, direction: string) {
    await performRefresh({ cursor, direction }, undefined);
  }

  async function handleWorkflowPageChange(cursor: RecordCursor, direction: string) {
    await performRefresh(undefined, { cursor, direction });
  }
</script>

<!-- Panel Container -->
<div class="rounded-base border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] overflow-hidden bg-white">

  <!-- Collapsible Header -->
  <button
    type="button"
    class="w-full flex items-center justify-between px-5 py-4 bg-primary-50 border-b-2 border-black hover:bg-primary-100 transition-colors duration-100 cursor-pointer"
    onclick={() => (isExpanded = !isExpanded)}
    aria-expanded={isExpanded}
  >
    <div class="flex items-center gap-3">
      <div class="p-2 bg-primary-500 border-2 border-black rounded-base shadow-small">
        <MessageSquareText class="w-4 h-4 text-white" />
      </div>
      <div class="flex flex-col items-start text-left">
        <div class="flex items-center gap-2">
          <span class="font-black text-base text-black uppercase tracking-tight">
            {promptCard.name}
          </span>
          <span class="badge bg-surface-50 text-primary-800 border border-black text-xs font-bold px-2 py-0.5 rounded-full">
            v{promptCard.version}
          </span>
          {#if monitoringData.status === 'success'}
            <span class="badge bg-green-100 text-green-800 border border-green-700 text-xs font-bold px-2 py-0.5 rounded-full">
              Active
            </span>
          {:else}
            <span class="badge bg-warning-100 text-warning-800 border border-warning-700 text-xs font-bold px-2 py-0.5 rounded-full">
              Unavailable
            </span>
          {/if}
        </div>
        <span class="text-xs text-slate-500 font-mono">{promptCard.space}/{promptCard.name}</span>
      </div>
    </div>

    <div class="flex items-center gap-3">
      <!-- Link to full prompt evaluation page -->
      <a
        href={promptEvalPath}
        target="_blank"
        rel="noopener noreferrer"
        class="p-1.5 rounded-base border-2 border-black bg-white hover:bg-surface-100 shadow-small transition-all duration-100"
        title="Open full evaluation page"
        onclick={(e) => e.stopPropagation()}
      >
        <ExternalLink class="w-3.5 h-3.5 text-primary-700" />
      </a>

      <!-- Refresh indicator -->
      {#if isRefreshing}
        <Loader2 class="w-4 h-4 animate-spin text-primary-600" />
      {/if}

      <!-- Chevron -->
      <svg
        class="w-4 h-4 text-slate-600 transition-transform duration-200 {isExpanded ? 'rotate-180' : ''}"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <polyline points="6 9 12 15 18 9" />
      </svg>
    </div>
  </button>

  <!-- Collapsible Body -->
  {#if isExpanded}
    <div class="transition-opacity duration-200 {isRefreshing ? 'opacity-60 pointer-events-none' : ''}">
      {#if monitoringData.status === 'error'}
        <!-- Compact error state for embedded panels -->
        <div class="p-6 flex items-start gap-4 bg-surface-50 border-t border-black/10">
          <div class="p-2 bg-warning-100 border-2 border-black rounded-base flex-shrink-0">
            <AlertCircle class="w-5 h-5 text-warning-800" />
          </div>
          <div class="flex-1">
            <p class="font-bold text-black mb-1">
              {monitoringData.errorKind === 'not_enabled'
                ? 'Scouter Not Enabled'
                : monitoringData.errorKind === 'not_found'
                  ? 'No Evaluation Profile'
                  : 'Error Loading Evaluation'}
            </p>
            <p class="text-sm text-slate-600 mb-3">{monitoringData.errorMsg}</p>
            {#if monitoringData.profile?.tasks}
              <GenAITaskAccordion tasks={monitoringData.profile.tasks} />
            {/if}
          </div>
        </div>
      {:else}
        <!-- Full dashboard for this prompt -->
        <div class="pt-4">
          <GenAIDashboard
            bind:monitoringData
            onRecordPageChange={handleRecordPageChange}
            onWorkflowPageChange={handleWorkflowPageChange}
          />
        </div>
      {/if}
    </div>
  {/if}
</div>
