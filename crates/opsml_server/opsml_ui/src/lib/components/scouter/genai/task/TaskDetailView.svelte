<script lang="ts">
  import { getAssertion, type GenAIEvalTaskResult } from '../task';
  import { Info, Activity, AlertCircle, GitBranch, CheckCircle2, XCircle, TrendingUp, MessageSquareText } from 'lucide-svelte';
  import Pill from '$lib/components/utils/Pill.svelte';
  import ComparisonView from './ComparisonView.svelte';
  import type { TraceAssertion } from '../task';
  import TraceAssertionPill from './TraceAssertionPill.svelte';
  import type { GenAIEvalProfile } from '../types';
  import { GenAIEvalProfileHelper } from '../utils';
  import PromptModal from '$lib/components/card/prompt/common/PromptModal.svelte';

  let { task, profile } = $props<{
    task: GenAIEvalTaskResult;
    profile: GenAIEvalProfile;
  }>();

  const active_task: GenAIEvalTaskResult = $derived(task);
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
      ? GenAIEvalProfileHelper.getLLMJudgeById(profile, active_task.task_id)
      : null
  );


  function formatTimestamp(timestamp: string): string {
    return new Date(timestamp).toLocaleTimeString('en-US', {
        hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit", fractionalSecondDigits: 3
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

  // Status Bar Color logic
  const statusColor = $derived.by(() => {
    if (isConditional) return 'bg-tertiary-500';
    return active_task.passed ? 'bg-secondary-500' : 'bg-error-600';
  });

  const statusLabel = $derived.by(() => {
     if (isConditional) return 'CONDITIONAL';
     return active_task.passed ? 'PASSED' : 'FAILED';
  });

  // Dynamic Theme for the Message Box (Fixes the "Always Red" bug)
  const messageTheme = $derived.by(() => {
    if (isConditional) {
      return {
        color: '#0d9488', // Tertiary/Teal
        borderColor: 'border-tertiary-600',
        textColor: 'text-tertiary-900',
        bgColor: 'bg-tertiary-50',
        title: 'Logic Message'
      };
    } else if (active_task.passed) {
      return {
        color: '#16a34a', // Secondary/Green
        borderColor: 'border-secondary-600',
        textColor: 'text-secondary-900',
        bgColor: 'bg-secondary-50',
        title: 'Success Message'
      };
    } else {
      return {
        color: '#d93025', // Error/Red
        borderColor: 'border-error-600',
        textColor: 'text-error-900',
        bgColor: 'bg-error-50',
        title: 'Failure Reason'
      };
    }
  });
</script>

<div class="flex flex-col h-full bg-white">

  <div class="p-3 border-b-2 border-black bg-surface-50">
    <div class="flex items-start gap-2">
      <div class={`w-1 h-14 rounded ${statusColor}`}></div>

      <div class="flex-1 min-w-0">
        <h3 class="font-bold text-gray-900 truncate">{active_task.task_id}</h3>
        <p class="text-sm text-gray-600">{active_task.task_type}</p>
        <p class="text-xs font-mono text-gray-500 mt-1">{active_task.record_uid.slice(0, 16)}...</p>
      </div>

      <div class="mr-2 mt-1">
        {#if isConditional}
            <GitBranch class="w-6 h-6 text-tertiary-600"/>
        {:else if active_task.passed}
            <CheckCircle2 class="w-6 h-6 text-secondary-600"/>
        {:else}
            <XCircle class="w-6 h-6 text-error-600"/>
        {/if}
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
        <Pill
            key="Status"
            value={statusLabel}
            textSize="text-xs"
            bgColor={isConditional ? 'bg-tertiary-100' : active_task.passed ? 'bg-secondary-100' : 'bg-error-100'}
            textColor={isConditional ? 'text-tertiary-900' : active_task.passed ? 'text-secondary-900' : 'text-error-900'}
            borderColor={isConditional ? 'border-tertiary-900' : active_task.passed ? 'border-secondary-900' : 'border-error-900'}
        />

        <Pill key="Type" value={active_task.task_type} textSize="text-xs"/>
        <Pill key="Stage" value={active_task.stage.toString()} textSize="text-xs"/>
        <Pill key="Operator" value={active_task.operator} textSize="text-xs"/>
      </div>
    </section>

    {#if active_task.task_type === 'Assertion' || active_task.task_type === 'TraceAssertion' || active_task.task_type === 'LLMJudge'}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
          <Activity color="#8059b6"/>
          <header class="pl-2 text-primary-950 text-sm font-bold">Assertion Target</header>
        </div>

        <div class="flex flex-wrap gap-2">
          {#if isTraceAssertion}
            <TraceAssertionPill assertion={assertion as TraceAssertion} />
          {:else if fieldPath}
            <Pill key="Field Path" value={fieldPath} textSize="text-xs"/>
          {:else}
            <Pill key="Field Path" value="Root" textSize="text-xs" bgColor="bg-surface-200"/>
          {/if}
        </div>
      </section>
    {/if}

    {#if judgeTask}
      <section>
        <div class="flex flex-row items-center justify-between pb-2 mb-3 border-b-2 border-black">
          <div class="flex items-center">
            <MessageSquareText color="#8059b6"/>
            <header class="pl-2 text-primary-950 text-sm font-bold">LLM Judge Prompt</header>
          </div>
        </div>

        <div class="flex flex-col gap-2">
          <PromptModal prompt={judgeTask.prompt} />
          
          {#if judgeTask.max_retries}
            <Pill key="Max Retries" value={judgeTask.max_retries.toString()} textSize="text-xs" />
          {/if}
        </div>
      </section>
    {/if}

    <section>
      <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
        <Activity color="#8059b6"/>
        <header class="pl-2 text-primary-950 text-sm font-bold">Timing</header>
      </div>

      <div class="flex flex-col space-y-1 text-sm">
        <Pill key="Start Time" value={formatTimestamp(active_task.start_time)} textSize="text-xs"/>
        <Pill key="End Time" value={formatTimestamp(active_task.end_time)} textSize="text-xs"/>
        <Pill key="Duration" value={formatDuration(active_task.start_time, active_task.end_time)} textSize="text-xs"/>
      </div>
    </section>

    <section>
       <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
        <TrendingUp color="#8059b6"/>
        <header class="pl-2 text-primary-950 text-sm font-bold">Evaluation Result</header>
      </div>
      <div class="flex flex-wrap gap-2 text-xs">
        <Pill key="Score / Value" value={active_task.value.toFixed(4)} textSize="text-xs" />
      </div>
    </section>

    {#if (active_task.expected !== null || active_task.actual !== null)}
      <ComparisonView
        expected={active_task.expected}
        actual={active_task.actual}
        label={`Assertion: ${active_task.operator}`}
      />
    {/if}

    {#if active_task.message}
      <section>
        <div class={`flex flex-row items-center pb-2 mb-3 border-b-2 ${messageTheme.borderColor}`}>
          <AlertCircle color={messageTheme.color}/>
          <header class={`pl-2 text-sm font-bold ${messageTheme.textColor}`.replace('900', '600')}>
            {messageTheme.title}
          </header>
        </div>

        <div class={`bg-surface-50 border-2 ${messageTheme.borderColor} rounded-base p-3 shadow-small`}>
          <p class={`text-sm ${messageTheme.textColor} font-mono whitespace-pre-wrap`}>{active_task.message}</p>
        </div>
      </section>
    {/if}

  </div>
</div>