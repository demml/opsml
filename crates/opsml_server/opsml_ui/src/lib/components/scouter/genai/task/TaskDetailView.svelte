<script lang="ts">
  import type { GenAIEvalTaskResult } from '../task';
  import { Info, Tags, Activity, FileJson, AlertCircle, TrendingUp } from 'lucide-svelte';
  import Pill from '$lib/components/utils/Pill.svelte';
  import CodeBlock from '$lib/components/codeblock/CodeBlock.svelte';

  let {
    task,
    allTasks,
  }: {
    task: GenAIEvalTaskResult;
    allTasks: GenAIEvalTaskResult[];
  } = $props();

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

  function formatDuration(startTime: string, endTime: string): string {
    const start = new Date(startTime).getTime();
    const end = new Date(endTime).getTime();
    const durationMs = end - start;
    const seconds = durationMs / 1000;
    return seconds < 1 ? `${durationMs}ms` : `${seconds.toFixed(2)}s`;
  }

  function formatJsonValue(value: any): string {
    if (typeof value === 'object' && value !== null) {
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  }

  const hasError = $derived(!task.passed);
  const hasFieldPath = $derived(task.field_path !== null && task.field_path !== '');
  const isConditional = $derived(task.condition);
</script>

<div class="flex flex-col h-full bg-white">
  <div class="p-3 border-b-2 border-black bg-surface-50">
    <div class="flex items-start gap-2">
      <div class={`w-1 h-14 rounded ${hasError ? 'bg-error-600' : 'bg-success-600'}`}></div>
      <div class="flex-1 min-w-0">
        <h3 class="font-bold text-gray-900 truncate">{task.task_id}</h3>
        <p class="text-sm text-gray-600">{task.task_type}</p>
        <p class="text-xs font-mono text-gray-500 mt-1">{task.record_uid.slice(0, 16)}...</p>
      </div>
    </div>
  </div>

  <div class="flex-1 overflow-auto p-4 space-y-4">
    <section>
      <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
        <Info color="#8059b6"/>
        <header class="pl-2 text-primary-950 text-sm font-bold">Task Info</header>
      </div>

      <div class="flex flex-wrap gap-2 text-xs">
        <Pill key="Status" value={task.passed ? 'PASSED' : 'FAILED'} textSize="text-xs" bgColor={task.passed ? 'bg-success-100' : 'bg-error-100'} textColor={task.passed ? 'text-success-900' : 'text-error-900'} borderColor={task.passed ? 'border-success-900' : 'border-error-900'} />
        <Pill key="Type" value={task.task_type} textSize="text-xs"/>
        <Pill key="Stage" value={task.stage.toString()} textSize="text-xs"/>
        <Pill key="Operator" value={task.operator} textSize="text-xs"/>
        {#if isConditional}
          <Pill key="Conditional" value="Yes" textSize="text-xs" bgColor="bg-warning-100" textColor="text-warning-900" borderColor="border-warning-900" />
        {/if}
      </div>
    </section>

    <section>
      <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
        <Activity color="#8059b6"/>
        <header class="pl-2 text-primary-950 text-sm font-bold">Timing</header>
      </div>

      <div class="flex flex-col space-y-1 text-sm">
        <Pill key="Created" value={formatTimestamp(task.created_at)} textSize="text-xs"/>
        <Pill key="Start Time" value={formatTimestamp(task.start_time)} textSize="text-xs"/>
        <Pill key="End Time" value={formatTimestamp(task.end_time)} textSize="text-xs"/>
        <Pill key="Duration" value={formatDuration(task.start_time, task.end_time)} textSize="text-xs"/>
      </div>
    </section>

    <section>
      <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
        <TrendingUp color="#8059b6"/>
        <header class="pl-2 text-primary-950 text-sm font-bold">Evaluation Result</header>
      </div>

      <div class="flex flex-col space-y-1 text-sm">
        <Pill key="Value" value={task.value.toFixed(4)} textSize="text-xs"/>
        {#if hasFieldPath}
          <Pill key="Field Path" value={task.field_path || 'N/A'} textSize="text-xs"/>
        {/if}
      </div>
    </section>

    {#if task.expected !== null && task.expected !== undefined}
      {#key task.task_id}
        <section>
          <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
            <FileJson color="#8059b6"/>
            <header class="pl-2 text-primary-950 text-sm font-bold">Expected Value</header>
          </div>
          <div class="bg-surface-50 rounded-base border-2 border-black p-1 shadow-small text-xs">
            <CodeBlock
              code={formatJsonValue(task.expected)}
              showLineNumbers={false}
              lang="json"
              prePadding="p-1"
            />
          </div>
        </section>
      {/key}
    {/if}

    {#if task.actual !== null && task.actual !== undefined}
      {#key task.task_id}
        <section>
          <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
            <FileJson color="#8059b6"/>
            <header class="pl-2 text-primary-950 text-sm font-bold">Actual Value</header>
          </div>
          <div class="bg-surface-50 rounded-base border-2 border-black p-1 shadow-small text-xs">
            <CodeBlock
              code={formatJsonValue(task.actual)}
              showLineNumbers={false}
              lang="json"
              prePadding="p-1"
            />
          </div>
        </section>
      {/key}
    {/if}

    {#if task.message}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
          <Tags color="#8059b6"/>
          <header class="pl-2 text-primary-950 text-sm font-bold">Message</header>
        </div>
        <div class="bg-surface-50 border-2 border-black rounded-base p-3 shadow-small">
          <p class="text-sm text-gray-700">{task.message}</p>
        </div>
      </section>
    {/if}

    {#if hasError}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-error-600">
          <AlertCircle color="#d93025"/>
          <header class="pl-2 text-error-600 text-sm font-bold">Failure Details</header>
        </div>

        <div class="bg-error-50 border-2 border-error-600 rounded-base p-3 shadow-small">
          <p class="text-sm text-error-600 font-medium mb-2">This task did not pass evaluation.</p>
          <div class="space-y-1 text-xs">
            <div class="flex gap-2">
              <span class="font-bold text-error-800">Operator:</span>
              <span class="text-error-700">{task.operator}</span>
            </div>
            {#if task.message}
              <div class="flex gap-2">
                <span class="font-bold text-error-800">Message:</span>
                <span class="text-error-700">{task.message}</span>
              </div>
            {/if}
          </div>
        </div>
      </section>
    {/if}
  </div>
</div>