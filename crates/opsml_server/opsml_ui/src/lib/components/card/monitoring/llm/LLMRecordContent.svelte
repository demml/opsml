<script lang="ts">
  import { X, Info, Activity, FileJson, AlertCircle, BarChart3 } from 'lucide-svelte';
  import type { LLMDriftServerRecord, Score, ScoreMap } from './llm';
  import { Status } from './llm';
  import CodeBlock from '$lib/components/codeblock/CodeBlock.svelte';
  import Pill from '$lib/components/utils/Pill.svelte';

  let {
    record,
    onClose,
    showCloseButton = true,
  }: {
    record: LLMDriftServerRecord;
    onClose?: () => void;
    showCloseButton?: boolean;
  } = $props();

  function getStatusColor(status: Status): string {
    switch (status) {
      case Status.Processed:
        return 'bg-secondary-600';
      case Status.Processing:
        return 'bg-primary-600';
      case Status.Pending:
        return 'bg-warning-600';
      case Status.Failed:
        return 'bg-error-600';
      default:
        return 'bg-gray-400';
    }
  }

  function getStatusLabel(status: Status): string {
    const labels: Record<Status, string> = {
      [Status.All]: 'ALL',
      [Status.Pending]: 'PENDING',
      [Status.Processing]: 'PROCESSING',
      [Status.Processed]: 'PROCESSED',
      [Status.Failed]: 'FAILED',
    };
    return labels[status] || 'UNKNOWN';
  }

  function formatTimestamp(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
  }

  function formatDuration(duration?: number): string {
    if (duration === undefined) return 'N/A';
    const seconds = duration / 1000;
    return seconds < 1 ? `${duration}ms` : `${seconds.toFixed(2)}s`;
  }

  const hasError = $derived(record.status === Status.Failed);
  const hasPrompt = $derived(record.prompt && record.prompt.trim().length > 0);
  const hasContext = $derived(record.context && record.context.trim().length > 0);
  const hasScore = $derived(record.score && Object.keys(record.score).length > 0);
  const scoreEntries = $derived(
    hasScore ? Object.entries(record.score).sort((a, b) => b[1].score - a[1].score) : []
  );
</script>

<div class="flex flex-col h-full bg-white">
  <!-- Header -->
  <div class="flex items-start justify-between p-6 border-b-2 border-black bg-surface-50 gap-6 flex-shrink-0">
    <div class="flex flex-col gap-4 flex-1 min-w-0">
      <div class="flex items-center gap-3">
        <div class={`w-2 h-10 rounded flex-shrink-0 ${getStatusColor(record.status)}`}></div>
        <div class="min-w-0 flex-1">
          <h2 class="text-lg font-bold text-primary-800">LLM Drift Record</h2>
          <p class="text-sm font-mono text-gray-600 truncate">{record.uid}</p>
        </div>
      </div>

      <div class="flex flex-wrap gap-1">
        <span class="badge text-primary-900 border-black border-1 shadow-small bg-primary-100">
          ID: {record.id}
        </span>
        <span class="badge border-black border-1 shadow-small {record.status === Status.Failed ? 'bg-error-100 text-error-900' : 'bg-success-100 text-success-900'}">
          {getStatusLabel(record.status)}
        </span>
      </div>
    </div>

    <div class="flex gap-2 flex-shrink-0">
      {#if showCloseButton && onClose}
        <button
          onclick={onClose}
          class="p-2 bg-primary-800 text-white hover:bg-primary-500 rounded-lg transition-colors border-2 border-black shadow-small"
          aria-label="Close panel"
        >
          <X class="w-6 h-6" />
        </button>
      {/if}
    </div>
  </div>

  <!-- Scrollable Content -->
  <div class="flex-1 overflow-auto p-4 space-y-4">

    <!-- Record Info -->
    <section>
      <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
        <Info color="#8059b6"/>
        <header class="pl-2 text-primary-950 text-sm font-bold">Record Info</header>
      </div>

      <div class="flex flex-wrap gap-2 text-xs">
        <Pill key="Space" value={record.space} textSize="text-xs"/>
        <Pill key="Name" value={record.name} textSize="text-xs"/>
        <Pill key="Version" value={record.version} textSize="text-xs"/>
      </div>
    </section>

    <!-- Timing Information -->
    <section>
      <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
        <Activity color="#8059b6"/>
        <header class="pl-2 text-primary-950 text-sm font-bold">Timing</header>
      </div>

      <div class="flex flex-col space-y-1 text-sm">
        <Pill key="Created" value={formatTimestamp(record.created_at)} textSize="text-xs"/>
        <Pill key="Updated" value={formatTimestamp(record.updated_at)} textSize="text-xs"/>
        
        {#if record.processing_started_at}
          <Pill key="Processing Started" value={formatTimestamp(record.processing_started_at)} textSize="text-xs"/>
        {/if}
        
        {#if record.processing_ended_at}
          <Pill key="Processing Ended" value={formatTimestamp(record.processing_ended_at)} textSize="text-xs"/>
        {/if}
        
        {#if record.processing_duration !== undefined}
          <Pill key="Processing Duration" value={formatDuration(record.processing_duration)} textSize="text-xs"/>
        {/if}
      </div>
    </section>

    <!-- Scores -->
    {#if hasScore}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
          <BarChart3 color="#8059b6"/>
          <header class="pl-2 text-primary-950 text-sm font-bold">Evaluation Scores ({scoreEntries.length})</header>
        </div>

        <div class="space-y-3">
          {#each scoreEntries as [metricName, scoreData]}
            <div class="bg-surface-50 border-2 border-black rounded-base p-3 shadow-small">
              <!-- Metric Header with Score -->
              <div class="flex items-start justify-between gap-3 mb-2">
                <h4 class="text-sm font-bold text-gray-900 flex-1">{metricName}</h4>
                <span class="px-3 py-1 rounded text-sm font-bold border-2 bg-primary-100 border-primary-800 text-primary-900 flex-shrink-0">
                  {scoreData.score}
                </span>
              </div>

              <!-- Reason -->
              {#if scoreData.reason && scoreData.reason.trim().length > 0}
                <div class="text-xs text-gray-700 bg-primary-100 p-2 rounded border border-gray-300">
                  <span class="font-bold text-gray-900">Reason:</span> {scoreData.reason}
                </div>
              {/if}
            </div>
          {/each}
        </div>
      </section>
    {:else}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
          <BarChart3 color="#8059b6"/>
          <header class="pl-2 text-primary-950 text-sm font-bold">Evaluation Scores</header>
        </div>
        <div class="bg-surface-50 rounded-base border-2 border-black p-3 shadow-small">
          <p class="text-sm text-gray-500 italic">No evaluation scores available</p>
        </div>
      </section>
    {/if}

    <!-- Prompt -->
    {#if hasPrompt}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
          <FileJson color="#8059b6"/>
          <header class="pl-2 text-primary-950 text-sm font-bold">Prompt</header>
        </div>
        <div class="bg-surface-50 rounded-base border-2 border-black p-1 shadow-small text-xs">
          <CodeBlock
            code={record.prompt || ''}
            showLineNumbers={false}
            lang="text"
            prePadding="p-1"
          />
        </div>
      </section>
    {/if}

    <!-- Context -->
    {#if hasContext}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
          <FileJson color="#8059b6"/>
          <header class="pl-2 text-primary-950 text-sm font-bold">Context</header>
        </div>
        <div class="bg-surface-50 rounded-base border-2 border-black p-1 shadow-small text-xs">
          <CodeBlock
            code={record.context}
            showLineNumbers={false}
            lang="json"
            prePadding="p-1"
          />
        </div>
      </section>
    {/if}

    <!-- Error Details -->
    {#if hasError}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-error-600">
          <AlertCircle color="#d93025"/>
          <header class="pl-2 text-error-600 text-sm font-bold">Error Details</header>
        </div>

        <div class="bg-error-50 border-2 border-error-600 rounded-base p-3 shadow-small">
          <p class="text-sm text-error-600">
            Record processing failed. Please check the logs for more details.
          </p>
        </div>
      </section>
    {/if}

  </div>
</div>