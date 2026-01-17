<script lang="ts">
  import { X, Info, Activity, FileJson, AlertCircle, Hash } from 'lucide-svelte';
  import type { GenAIEvalRecord } from '../types';
  import { Status } from '../types';
  import CodeBlock from '$lib/components/codeblock/CodeBlock.svelte';
  import Pill from '$lib/components/utils/Pill.svelte';

  let {
    record,
    onClose,
    showCloseButton = true,
  }: {
    record: GenAIEvalRecord;
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

  function formatTimestamp(timestamp: string | null): string {
    if (!timestamp) return 'N/A';
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

  function formatDuration(duration: number | null): string {
    if (duration === null) return 'N/A';
    const seconds = duration / 1000;
    return seconds < 1 ? `${duration}ms` : `${seconds.toFixed(2)}s`;
  }

  const hasError = $derived(record.status === Status.Failed);
  const hasContext = $derived(
    record.context &&
    typeof record.context === 'object' &&
    Object.keys(record.context).length > 0
  );
  const contextString = $derived(
    hasContext ? JSON.stringify(record.context, null, 2) : ''
  );
</script>

<div class="flex flex-col h-full bg-white">
  <div class="flex items-start justify-between p-6 border-b-2 border-black bg-surface-50 gap-6 flex-shrink-0">
    <div class="flex flex-col gap-4 flex-1 min-w-0">
      <div class="flex items-center gap-3">
        <div class={`w-2 h-10 rounded flex-shrink-0 ${getStatusColor(record.status)}`}></div>
        <div class="min-w-0 flex-1">
          <h2 class="text-lg font-bold text-primary-800">GenAI Evaluation Record</h2>
          <p class="text-sm font-mono text-gray-600 truncate">{record.uid}</p>
        </div>
      </div>

      <div class="flex flex-wrap gap-1">
        <span class="badge text-primary-900 border-black border-1 shadow-small bg-primary-100">
          ID: {record.id}
        </span>
        <span class="badge border-black border-1 shadow-small {record.status === Status.Failed ? 'bg-error-100 text-error-900' : 'bg-secondary-100 text-secondary-900'}">
          {getStatusLabel(record.status)}
        </span>
        <span class="badge text-primary-900 border-black border-1 shadow-small bg-primary-100">
          {record.entity_type}
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

  <div class="flex-1 overflow-auto p-4 space-y-4">
    <section>
      <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
        <Info color="#8059b6"/>
        <header class="pl-2 text-primary-950 text-sm font-bold">Record Info</header>
      </div>

      <div class="flex flex-wrap gap-2 text-xs">
        <Pill key="Record ID" value={record.record_id} textSize="text-xs"/>
      </div>
    </section>

    <section>
      <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
        <Activity color="#8059b6"/>
        <header class="pl-2 text-primary-950 text-sm font-bold">Timing</header>
      </div>

      <div class="flex flex-col space-y-1 text-sm">
        <Pill key="Created" value={formatTimestamp(record.created_at)} textSize="text-xs"/>

        {#if record.updated_at}
          <Pill key="Updated" value={formatTimestamp(record.updated_at)} textSize="text-xs"/>
        {/if}

        {#if record.processing_started_at}
          <Pill key="Processing Started" value={formatTimestamp(record.processing_started_at)} textSize="text-xs"/>
        {/if}

        {#if record.processing_ended_at}
          <Pill key="Processing Ended" value={formatTimestamp(record.processing_ended_at)} textSize="text-xs"/>
        {/if}

        {#if record.processing_duration !== null}
          <Pill key="Processing Duration" value={formatDuration(record.processing_duration)} textSize="text-xs"/>
        {/if}
      </div>
    </section>

    {#if hasContext}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
          <FileJson color="#8059b6"/>
          <header class="pl-2 text-primary-950 text-sm font-bold">Context</header>
        </div>
        <div class="bg-surface-50 rounded-base border-2 border-black p-1 shadow-small text-xs">
          <CodeBlock
            code={contextString}
            showLineNumbers={false}
            lang="json"
            prePadding="p-1"
          />
        </div>
      </section>
    {/if}

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