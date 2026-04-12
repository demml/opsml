<script lang="ts">
  import { getAssertion, type EvalTaskResult } from '../task';
  import { Info, Activity, AlertCircle, GitBranch, CheckCircle2, XCircle, TrendingUp, MessageSquareText } from 'lucide-svelte';
  import Pill from '$lib/components/utils/Pill.svelte';
  import ComparisonView from './ComparisonView.svelte';
  import type { TraceAssertion } from '../task';
  import TraceAssertionPill from './TraceAssertionPill.svelte';
  import type { AgentEvalProfile } from '../types';
  import { AgentEvalProfileHelper } from '../utils';
  import PromptModal from '$lib/components/card/prompt/common/PromptModal.svelte';

  let { task, profile } = $props<{
    task: EvalTaskResult;
    profile: AgentEvalProfile;
  }>();

  const active_task: EvalTaskResult = $derived(task);
  const assertion = $derived(getAssertion(task));

  const isTraceAssertion = $derived(
    typeof assertion !== 'string' && assertion !== null
  );

  const fieldPath = $derived(
    typeof assertion === 'string' || assertion === null
      ? assertion
      : null
  );

  const judgeTask = $derived(
    active_task.task_type === 'LLMJudge'
      ? AgentEvalProfileHelper.getLLMJudgeById(profile, active_task.task_id)
      : null
  );

  function formatTimestamp(timestamp: string): string {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit', fractionalSecondDigits: 3
    });
  }

  function formatDuration(startTime: string, endTime: string): string {
    const start = new Date(startTime).getTime();
    const end = new Date(endTime).getTime();
    const durationMs = end - start;
    const seconds = durationMs / 1000;
    return seconds < 1 ? `${durationMs}ms` : `${seconds.toFixed(2)}s`;
  }

  const isConditional = $derived(active_task.condition);

  const statusColor = $derived.by(() => {
    if (isConditional) return 'bg-tertiary-500';
    return active_task.passed ? 'bg-secondary-500' : 'bg-error-600';
  });

  const statusLabel = $derived.by(() => {
    if (isConditional) return 'CONDITIONAL';
    return active_task.passed ? 'PASSED' : 'FAILED';
  });

  // Message box theme — class-only, no hex values
  const messageTheme = $derived.by(() => {
    if (isConditional) {
      return {
        iconClass: 'text-tertiary-600',
        borderColor: 'border-tertiary-600',
        textColor: 'text-tertiary-900',
        bgColor: 'bg-tertiary-50',
        title: 'Logic Message'
      };
    } else if (active_task.passed) {
      return {
        iconClass: 'text-secondary-600',
        borderColor: 'border-secondary-600',
        textColor: 'text-secondary-900',
        bgColor: 'bg-secondary-50',
        title: 'Success Message'
      };
    } else {
      return {
        iconClass: 'text-error-600',
        borderColor: 'border-error-600',
        textColor: 'text-error-900',
        bgColor: 'bg-error-50',
        title: 'Failure Reason'
      };
    }
  });
</script>

<div class="flex flex-col h-full bg-surface-50">

  <!-- Task header -->
  <div class="flex-shrink-0 p-3 border-b-2 border-black bg-surface-50">
    <div class="flex items-start gap-2">
      <div class={`w-1 h-14 rounded flex-shrink-0 ${statusColor}`}></div>
      <div class="flex-1 min-w-0">
        <h3 class="font-bold text-primary-950 truncate">{active_task.task_id}</h3>
        <p class="text-sm text-primary-700">{active_task.task_type}</p>
        <p class="text-xs font-mono text-primary-600 mt-1">{active_task.record_uid.slice(0, 16)}…</p>
      </div>
      <div class="mr-2 mt-1 flex-shrink-0">
        {#if isConditional}
          <GitBranch class="w-6 h-6 text-tertiary-600" />
        {:else if active_task.passed}
          <CheckCircle2 class="w-6 h-6 text-secondary-600" />
        {:else}
          <XCircle class="w-6 h-6 text-error-600" />
        {/if}
      </div>
    </div>
  </div>

  <div class="flex-1 overflow-auto p-4 space-y-4">

    <!-- Task Info -->
    <section>
      <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
        <Info class="w-4 h-4 text-primary-500" />
        <header class="pl-2 text-primary-950 text-sm font-bold">Task Info</header>
      </div>
      <div class="flex flex-wrap gap-2 text-xs">
        <Pill
          key="Status"
          value={statusLabel}
          textSize="text-xs"
          bgColor={isConditional ? 'bg-tertiary-100' : active_task.passed ? 'bg-secondary-100' : 'bg-error-100'}
          textColor={isConditional ? 'text-tertiary-900' : active_task.passed ? 'text-secondary-900' : 'text-error-900'}
          borderColor={isConditional ? 'border-tertiary-900' : active_task.passed ? 'border-secondary-900' : 'border-error-900'}
        />
        <Pill key="Type" value={active_task.task_type} textSize="text-xs" />
        <Pill key="Stage" value={active_task.stage.toString()} textSize="text-xs" />
        <Pill key="Operator" value={active_task.operator} textSize="text-xs" />
      </div>
    </section>

    <!-- Assertion Target -->
    {#if active_task.task_type === 'Assertion' || active_task.task_type === 'TraceAssertion' || active_task.task_type === 'LLMJudge'}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
          <Activity class="w-4 h-4 text-primary-500" />
          <header class="pl-2 text-primary-950 text-sm font-bold">Assertion Target</header>
        </div>
        <div class="flex flex-wrap gap-2">
          {#if isTraceAssertion}
            <TraceAssertionPill assertion={assertion as TraceAssertion} />
          {:else if fieldPath}
            <Pill key="Field Path" value={fieldPath} textSize="text-xs" />
          {:else}
            <Pill key="Field Path" value="Root" textSize="text-xs" bgColor="bg-surface-200" />
          {/if}
        </div>
      </section>
    {/if}

    <!-- LLM Judge Prompt -->
    {#if judgeTask}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
          <MessageSquareText class="w-4 h-4 text-primary-500" />
          <header class="pl-2 text-primary-950 text-sm font-bold">LLM Judge Prompt</header>
        </div>
        <div class="flex flex-col gap-2">
          <PromptModal prompt={judgeTask.prompt} />
          {#if judgeTask.max_retries}
            <Pill key="Max Retries" value={judgeTask.max_retries.toString()} textSize="text-xs" />
          {/if}
        </div>
      </section>
    {/if}

    <!-- Timing -->
    <section>
      <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
        <Activity class="w-4 h-4 text-primary-500" />
        <header class="pl-2 text-primary-950 text-sm font-bold">Timing</header>
      </div>
      <div class="flex flex-col space-y-1 text-sm">
        <Pill key="Start Time" value={formatTimestamp(active_task.start_time)} textSize="text-xs" />
        <Pill key="End Time" value={formatTimestamp(active_task.end_time)} textSize="text-xs" />
        <Pill key="Duration" value={formatDuration(active_task.start_time, active_task.end_time)} textSize="text-xs" />
      </div>
    </section>

    <!-- Evaluation Result -->
    <section>
      <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
        <TrendingUp class="w-4 h-4 text-primary-500" />
        <header class="pl-2 text-primary-950 text-sm font-bold">Evaluation Result</header>
      </div>
      <div class="flex flex-wrap gap-2 text-xs">
        <Pill key="Score / Value" value={active_task.value.toFixed(4)} textSize="text-xs" />
      </div>
    </section>

    <!-- Comparison: expected vs actual -->
    {#if (active_task.expected !== null || active_task.actual !== null)}
      <ComparisonView
        expected={active_task.expected}
        actual={active_task.actual}
        label={`Assertion: ${active_task.operator}`}
      />
    {/if}

    <!-- Result message -->
    {#if active_task.message}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 {messageTheme.borderColor}">
          <AlertCircle class="w-4 h-4 {messageTheme.iconClass}" />
          <header class="pl-2 text-sm font-bold {messageTheme.textColor}">
            {messageTheme.title}
          </header>
        </div>
        <div class="bg-surface-50 border-2 {messageTheme.borderColor} rounded-base p-3 shadow-small">
          <p class="text-sm {messageTheme.textColor} font-mono whitespace-pre-wrap">{active_task.message}</p>
        </div>
      </section>
    {/if}

  </div>
</div>
