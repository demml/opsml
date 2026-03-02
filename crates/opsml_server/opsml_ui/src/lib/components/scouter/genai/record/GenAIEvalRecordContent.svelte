<script lang="ts">
  import { X, FileJson, AlertCircle, Clock, Tag, ChevronDown, ChevronUp } from 'lucide-svelte';
  import type { GenAIEvalRecord } from '../types';
  import { Status } from '../types';
  import CodeBlock from '$lib/components/codeblock/CodeBlock.svelte';

  let {
    record,
    onClose,
    showCloseButton = true,
  }: {
    record: GenAIEvalRecord;
    onClose?: () => void;
    showCloseButton?: boolean;
  } = $props();

  let contextOpen = $state(true);

  function getStatusBadgeClass(status: Status): string {
    switch (status) {
      case Status.Processed:  return 'bg-secondary-100 text-secondary-900 border-black';
      case Status.Processing: return 'bg-primary-100 text-primary-900 border-black';
      case Status.Pending:    return 'bg-warning-300 text-black border-black';
      case Status.Failed:     return 'bg-error-100 text-error-900 border-black';
      default:                return 'bg-surface-200 text-primary-800 border-black';
    }
  }

  function getStatusBarColor(status: Status): string {
    switch (status) {
      case Status.Processed:  return 'bg-secondary-500';
      case Status.Processing: return 'bg-primary-500';
      case Status.Pending:    return 'bg-warning-300';
      case Status.Failed:     return 'bg-error-600';
      default:                return 'bg-surface-200';
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
    if (!timestamp) return '—';
    return new Date(timestamp).toLocaleString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true,
    });
  }

  function formatDuration(duration: number | null): string {
    if (duration === null) return '—';
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

  // Build the metadata table rows: always-present + conditional timing rows
  const metaRows = $derived((() => {
    const rows: Array<[string, string]> = [
      ['Record ID',    record.record_id],
      ['Entity ID',    record.id.toString()],
      ['Entity Type',  record.entity_type],
      ['Status',       getStatusLabel(record.status)],
      ['Created',      formatTimestamp(record.created_at)],
    ];
    if (record.updated_at)
      rows.push(['Updated', formatTimestamp(record.updated_at)]);
    if (record.processing_started_at)
      rows.push(['Proc. Started', formatTimestamp(record.processing_started_at)]);
    if (record.processing_ended_at)
      rows.push(['Proc. Ended', formatTimestamp(record.processing_ended_at)]);
    if (record.processing_duration !== null)
      rows.push(['Duration', formatDuration(record.processing_duration)]);
    return rows;
  })());
</script>

<div class="flex flex-col h-full bg-surface-50 overflow-hidden">

  <!-- Header -->
  <header class="flex-shrink-0 flex items-center justify-between px-4 py-2.5 border-b-2 border-black bg-primary-100 z-20 gap-4">

    <!-- Left: status bar + breadcrumb -->
    <div class="flex items-center gap-2 min-w-0">
      <div class="w-1 h-8 rounded flex-shrink-0 {getStatusBarColor(record.status)}"></div>
      <nav class="flex items-center gap-1.5 text-xs font-mono min-w-0" aria-label="breadcrumb">
        <span class="text-primary-600 font-bold uppercase tracking-wide">Record</span>
        <span class="text-primary-400">/</span>
        <span
          class="font-black text-primary-950 truncate max-w-[180px] sm:max-w-xs"
          title={record.uid}
        >{record.uid}</span>
      </nav>
    </div>

    <!-- Right: chips + close -->
    <div class="flex items-center gap-1.5 flex-shrink-0 flex-wrap justify-end">
      <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-surface-50 text-primary-800 rounded-base shadow-small">
        <Tag class="w-3 h-3" />
        {record.entity_type}
      </span>
      <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-black border-2 {getStatusBadgeClass(record.status)} rounded-base shadow-small uppercase tracking-wide">
        {getStatusLabel(record.status)}
      </span>
      {#if record.processing_duration !== null}
        <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-surface-50 text-primary-800 rounded-base shadow-small">
          <Clock class="w-3 h-3" />
          {formatDuration(record.processing_duration)}
        </span>
      {/if}
      {#if showCloseButton && onClose}
        <button
          onclick={onClose}
          class="p-1.5 border-2 border-black bg-primary-800 text-white hover:bg-primary-500 shadow-small shadow-click-small rounded-base transition-all duration-100"
          aria-label="Close"
        >
          <X class="w-4 h-4" />
        </button>
      {/if}
    </div>
  </header>

  <!-- Scrollable body -->
  <div class="flex-1 overflow-auto p-4 space-y-4">

    <!-- Record Info + Timing: compact alternating-row table -->
    <section>
      <div class="border-2 border-black rounded-base overflow-hidden shadow-small">
        <table class="w-full text-xs">
          <tbody>
            {#each metaRows as [label, value], i}
              <tr class="{i % 2 === 0 ? 'bg-surface-50' : 'bg-surface-200'}">
                <td class="px-2.5 py-1.5 font-black text-primary-800 uppercase tracking-wide border-b border-black/10 w-32 flex-shrink-0 whitespace-nowrap">
                  {label}
                </td>
                <td class="px-2.5 py-1.5 font-mono text-black border-b border-black/10 break-all">
                  {value}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </section>

    <!-- Context: collapsible dropdown -->
    {#if hasContext}
      <section>
        <div class="border-2 border-black rounded-base overflow-hidden shadow-small">
          <!-- Toggle header -->
          <button
            onclick={() => contextOpen = !contextOpen}
            class="w-full flex items-center justify-between px-3 py-2 bg-primary-100 hover:bg-primary-200 transition-colors duration-100 {contextOpen ? 'border-b-2 border-black' : ''}"
          >
            <div class="flex items-center gap-2">
              <FileJson class="w-3.5 h-3.5 text-primary-700" />
              <span class="text-xs font-black uppercase tracking-wide text-primary-900">Context</span>
            </div>
            {#if contextOpen}
              <ChevronUp class="w-3.5 h-3.5 text-primary-600" />
            {:else}
              <ChevronDown class="w-3.5 h-3.5 text-primary-600" />
            {/if}
          </button>

          {#if contextOpen}
            <div class="max-h-72 overflow-y-auto bg-surface-50 text-xs">
              <CodeBlock
                code={contextString}
                showLineNumbers={false}
                lang="json"
                prePadding="p-2"
              />
            </div>
          {/if}
        </div>
      </section>
    {/if}

    <!-- Error Details -->
    {#if hasError}
      <section>
        <div class="border-2 border-error-600 rounded-base overflow-hidden shadow-small">
          <div class="flex items-center gap-2 px-3 py-2 bg-error-100 border-b-2 border-error-600">
            <AlertCircle class="w-3.5 h-3.5 text-error-600" />
            <span class="text-xs font-black uppercase tracking-wide text-error-900">Error Details</span>
          </div>
          <div class="p-3 bg-error-50">
            <p class="text-xs text-error-900 font-mono">
              Record processing failed. Please check the logs for more details.
            </p>
          </div>
        </div>
      </section>
    {/if}

  </div>
</div>
