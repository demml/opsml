<script lang="ts">
  import {
    getAssertion,
    isAgentAssertionValue,
    isTraceAssertionValue,
    type AgentAssertion,
    type EvalTaskResult,
    type TraceAssertion,
  } from '../task';
  import { Accordion } from '@skeletonlabs/skeleton-svelte';
  import { Info, Activity, AlertCircle, GitBranch, CheckCircle2, XCircle, TrendingUp, MessageSquareText, ChevronDown } from 'lucide-svelte';
  import Pill from '$lib/components/utils/Pill.svelte';
  import ComparisonView from '$lib/components/scouter/agent/task/ComparisonView.svelte';
  import TraceAssertionPill from './TraceAssertionPill.svelte';
  import AgentAssertionPill from './AgentAssertionPill.svelte';
  import type { AgentEvalProfile } from '../types';
  import { AgentEvalProfileHelper } from '../utils';
  import PromptModal from '$lib/components/card/prompt/common/PromptModal.svelte';

  let { task, profile } = $props<{
    task: EvalTaskResult;
    profile: AgentEvalProfile;
  }>();

  const active_task: EvalTaskResult = $derived(task);
  const assertion = $derived(getAssertion(task));

  const isTraceAssertion = $derived(isTraceAssertionValue(assertion));
  const isAgentAssertion = $derived(isAgentAssertionValue(assertion));

  const fieldPath = $derived.by((): string | null => {
    if (isTraceAssertionValue(assertion) || isAgentAssertionValue(assertion)) {
      return null;
    }

    return assertion;
  });

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
  const durationStr = $derived(formatDuration(active_task.start_time, active_task.end_time));
  const showAssertionTarget = $derived(
    active_task.task_type === 'Assertion' ||
      active_task.task_type === 'TraceAssertion' ||
      active_task.task_type === 'LLMJudge' ||
      active_task.task_type === 'AgentAssertion'
  );
  const showComparison = $derived(
    active_task.expected !== null || active_task.actual !== null
  );

  const statusColor = $derived.by(() => {
    if (isConditional) return 'bg-tertiary-500';
    return active_task.passed ? 'bg-secondary-500' : 'bg-error-600';
  });

  const statusLabel = $derived.by(() => {
    if (isConditional) return 'CONDITIONAL';
    return active_task.passed ? 'PASSED' : 'FAILED';
  });

  const statusPillColors = $derived.by(() => {
    if (isConditional) {
      return { bg: 'bg-tertiary-100', text: 'text-tertiary-900', border: 'border-tertiary-900' };
    }
    if (active_task.passed) {
      return { bg: 'bg-secondary-100', text: 'text-secondary-900', border: 'border-secondary-900' };
    }
    return { bg: 'bg-error-100', text: 'text-error-900', border: 'border-error-900' };
  });

  const metadataRows = $derived.by(() => [
    { key: 'Status', value: statusLabel },
    { key: 'Type', value: active_task.task_type },
    { key: 'Stage', value: active_task.stage.toString() },
    { key: 'Operator', value: active_task.operator },
    { key: 'Start Time', value: formatTimestamp(active_task.start_time) },
    { key: 'End Time', value: formatTimestamp(active_task.end_time) },
    { key: 'Duration', value: durationStr },
    { key: 'Score', value: active_task.value.toFixed(4) },
  ]);

  const defaultOpenValues = $derived.by((): string[] => {
    const open: string[] = [];
    if (showAssertionTarget) open.push('assertion-target');
    if (showComparison) open.push('comparison');
    if (active_task.message) open.push('result-message');
    return open;
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

  <!-- Summary Header: always visible -->
  <div class="flex-shrink-0 p-3 border-b-2 border-black bg-surface-50">
    <div class="flex items-start gap-2">
      <div class={`w-1 h-14 rounded flex-shrink-0 ${statusColor}`}></div>
      <div class="flex-1 min-w-0">
        <h3 class="font-bold text-primary-950 truncate">{active_task.task_id}</h3>
        <p class="text-xs font-mono text-primary-600 mt-0.5">{active_task.record_uid.slice(0, 16)}...</p>
        <div class="flex flex-wrap gap-1.5 mt-2">
          <Pill key="Type" value={active_task.task_type} textSize="text-xs" />
          <Pill
            key="Status"
            value={statusLabel}
            textSize="text-xs"
            bgColor={statusPillColors.bg}
            textColor={statusPillColors.text}
            borderColor={statusPillColors.border}
          />
          <Pill key="Duration" value={durationStr} textSize="text-xs" />
          <Pill key="Score" value={active_task.value.toFixed(4)} textSize="text-xs" />
        </div>
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

  <!-- Scrollable accordion body -->
  <div class="flex-1 overflow-auto">
    {#key active_task.task_id}
      <Accordion defaultValue={defaultOpenValues} multiple collapsible spaceY="" rounded="" classes="border-t-2 border-black">
        {#snippet iconClosed()}
          <ChevronDown class="w-4 h-4 text-primary-700 transition-transform duration-100 ease-out" />
        {/snippet}
        {#snippet iconOpen()}
          <ChevronDown class="w-4 h-4 text-primary-700 rotate-180 transition-transform duration-100 ease-out" />
        {/snippet}

        <Accordion.Item
          value="task-metadata"
          controlBase="w-full flex items-center justify-between px-4 py-2.5 border-b-2 border-black cursor-pointer transition-colors duration-100 bg-surface-100 text-primary-900"
          controlHover="hover:bg-primary-100"
          indicatorBase="pl-2"
          panelBase="p-0 bg-surface-50"
          spaceY=""
        >
          {#snippet control()}
            <div class="flex items-center gap-2">
              <Info class="w-4 h-4 text-primary-500" />
              <span class="text-xs font-black uppercase tracking-wide text-primary-800">Task Metadata</span>
            </div>
          {/snippet}

          {#snippet panel()}
            <div class="border-b-2 border-black">
              {#each metadataRows as row, i (row.key)}
                <div class="flex px-4 py-1.5 {i % 2 === 0 ? 'bg-surface-50' : 'bg-surface-300'}">
                  <span class="w-28 flex-shrink-0 text-xs font-bold uppercase text-primary-700">{row.key}</span>
                  <span class="text-xs font-mono text-primary-950">{row.value}</span>
                </div>
              {/each}
            </div>
          {/snippet}
        </Accordion.Item>

        {#if showAssertionTarget}
          <Accordion.Item
            value="assertion-target"
            controlBase="w-full flex items-center justify-between px-4 py-2.5 border-b-2 border-black cursor-pointer transition-colors duration-100 bg-surface-100 text-primary-900"
            controlHover="hover:bg-primary-100"
            indicatorBase="pl-2"
            panelBase="p-0 bg-surface-50"
            spaceY=""
          >
            {#snippet control()}
              <div class="flex items-center gap-2">
                <Activity class="w-4 h-4 text-primary-500" />
                <span class="text-xs font-black uppercase tracking-wide text-primary-800">Assertion Target</span>
              </div>
            {/snippet}

            {#snippet panel()}
              <div class="px-4 py-3 border-b-2 border-black">
                <div class="flex flex-wrap gap-2">
                  {#if isTraceAssertion}
                    <TraceAssertionPill assertion={assertion as TraceAssertion} />
                  {:else if isAgentAssertion}
                    <AgentAssertionPill assertion={assertion as AgentAssertion} />
                  {:else if fieldPath}
                    <Pill key="Field Path" value={fieldPath} textSize="text-xs" />
                  {:else}
                    <Pill key="Field Path" value="Root" textSize="text-xs" bgColor="bg-surface-200" />
                  {/if}
                </div>
              </div>
            {/snippet}
          </Accordion.Item>
        {/if}

        {#if judgeTask}
          <Accordion.Item
            value="judge-prompt"
            controlBase="w-full flex items-center justify-between px-4 py-2.5 border-b-2 border-black cursor-pointer transition-colors duration-100 bg-surface-100 text-primary-900"
            controlHover="hover:bg-primary-100"
            indicatorBase="pl-2"
            panelBase="p-0 bg-surface-50"
            spaceY=""
          >
            {#snippet control()}
              <div class="flex items-center gap-2">
                <MessageSquareText class="w-4 h-4 text-primary-500" />
                <span class="text-xs font-black uppercase tracking-wide text-primary-800">LLM Judge Prompt</span>
              </div>
            {/snippet}

            {#snippet panel()}
              <div class="px-4 py-3 border-b-2 border-black flex flex-col gap-2">
                <PromptModal prompt={judgeTask.prompt} />
                {#if judgeTask.max_retries}
                  <Pill key="Max Retries" value={judgeTask.max_retries.toString()} textSize="text-xs" />
                {/if}
              </div>
            {/snippet}
          </Accordion.Item>
        {/if}

        {#if showComparison}
          <Accordion.Item
            value="comparison"
            controlBase="w-full flex items-center justify-between px-4 py-2.5 border-b-2 border-black cursor-pointer transition-colors duration-100 bg-surface-100 text-primary-900"
            controlHover="hover:bg-primary-100"
            indicatorBase="pl-2"
            panelBase="p-0 bg-surface-50"
            spaceY=""
          >
            {#snippet control()}
              <div class="flex items-center gap-2">
                <TrendingUp class="w-4 h-4 text-primary-500" />
                <span class="text-xs font-black uppercase tracking-wide text-primary-800">Assertion: {active_task.operator}</span>
              </div>
            {/snippet}

            {#snippet panel()}
              <div class="px-4 py-3 border-b-2 border-black">
                <ComparisonView
                  expected={active_task.expected}
                  actual={active_task.actual}
                />
              </div>
            {/snippet}
          </Accordion.Item>
        {/if}

        {#if active_task.message}
          <Accordion.Item
            value="result-message"
            controlBase="w-full flex items-center justify-between px-4 py-2.5 border-b-2 {messageTheme.borderColor} cursor-pointer transition-colors duration-100 bg-surface-100"
            controlHover="hover:bg-primary-100"
            indicatorBase="pl-2"
            panelBase="p-0 bg-surface-50"
            spaceY=""
          >
            {#snippet control()}
              <div class="flex items-center gap-2">
                <AlertCircle class="w-4 h-4 {messageTheme.iconClass}" />
                <span class="text-xs font-black uppercase tracking-wide {messageTheme.textColor}">{messageTheme.title}</span>
              </div>
            {/snippet}

            {#snippet panel()}
              <div class="px-4 py-3 border-b-2 {messageTheme.borderColor}">
                <div class="bg-surface-50 border-2 {messageTheme.borderColor} rounded-base p-3 shadow-small">
                  <p class="text-sm {messageTheme.textColor} font-mono whitespace-pre-wrap">{active_task.message}</p>
                </div>
              </div>
            {/snippet}
          </Accordion.Item>
        {/if}
      </Accordion>
    {/key}
  </div>
</div>
