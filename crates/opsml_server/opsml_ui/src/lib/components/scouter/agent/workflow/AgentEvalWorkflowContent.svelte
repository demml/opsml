<script lang="ts">
  import { X, List, Clock, Layers, CheckCircle2, XCircle, Activity } from 'lucide-svelte';
  import { page } from '$app/state';
  import type { AgentEvalWorkflowResult, EvalTaskResult } from '../task';
  import WorkflowStageList from './WorkflowStageList.svelte';
  import TaskDetailView from '../task/TaskDetailView.svelte';
  import { getServerAgentEvalTask } from '../utils';
  import type { AgentEvalProfile, AgentEvalTaskRequest } from '../types';
  import { devMockStore } from '$lib/components/settings/mockMode.svelte';

  let {
    workflow,
    onClose,
    showCloseButton = true,
    profile,
    traceId,
  }: {
    workflow: AgentEvalWorkflowResult;
    onClose?: () => void;
    showCloseButton?: boolean;
    profile: AgentEvalProfile;
    traceId?: string;
  } = $props();

  const observabilityPath = $derived(
    traceId ? page.url.pathname.replace(/\/evaluation(\/.*)?$/, '/observability') : null
  );

  let selectedTask = $state<EvalTaskResult | null>(null);
  let tasks = $state<EvalTaskResult[]>([]);
  let activePanel = $state<'list' | 'detail'>('list');
  let loading = $state(true);

  async function loadTasks() {
    loading = true;
    try {
      if (devMockStore.enabled) {
        const { buildMockEvalTasks } = await import('$lib/components/scouter/evaluation/mockData');
        tasks = buildMockEvalTasks(workflow.record_uid);
        if (tasks.length > 0) selectedTask = tasks[0];
        return;
      }
      const request: AgentEvalTaskRequest = { record_uid: workflow.record_uid };
      const response = await getServerAgentEvalTask(fetch, request);
      tasks = response.tasks || [];
      if (tasks.length > 0) selectedTask = tasks[0];
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      loading = false;
    }
  }

  $effect(() => {
    loadTasks();
  });

  function handleTaskSelect(task: EvalTaskResult) {
    selectedTask = task;
    if (window.innerWidth < 1024) activePanel = 'detail';
  }

  function formatDuration(durationMs: number): string {
    const seconds = durationMs / 1000;
    return seconds < 1 ? `${durationMs}ms` : `${seconds.toFixed(2)}s`;
  }

  const totalStages = $derived(workflow.execution_plan.stages.length);

  const passRateBadgeClass = $derived(
    workflow.pass_rate >= 0.9
      ? 'bg-secondary-300 text-black border-black'
      : workflow.pass_rate >= 0.7
      ? 'bg-warning-300 text-black border-black'
      : 'bg-error-100 text-error-900 border-black'
  );
</script>

<div class="flex flex-col h-full bg-surface-50 overflow-hidden">

  <!-- ─── Header: matches TraceDetailContent aesthetic ───────────────────── -->
  <header class="flex-shrink-0 flex items-center justify-between px-4 py-2.5 border-b-2 border-black bg-primary-100 z-20 gap-4">

    <!-- Left: breadcrumb + record UID -->
    <div class="flex items-center gap-2 min-w-0">
      <nav class="flex items-center gap-1.5 text-xs font-mono min-w-0" aria-label="breadcrumb">
        <span class="text-primary-600 font-bold uppercase tracking-wide">Workflow</span>
        <span class="text-primary-400">/</span>
        <span
          class="font-black text-primary-950 truncate max-w-[180px] sm:max-w-xs"
          title={workflow.record_uid}
        >{workflow.record_uid}</span>
      </nav>
    </div>

    <!-- Right: metric chips + close -->
    <div class="flex items-center gap-1.5 flex-shrink-0 flex-wrap justify-end">
      <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-surface-50 text-primary-800 rounded-base shadow-small">
        <Layers class="w-3 h-3" />
        {workflow.total_tasks} tasks
      </span>
      <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-surface-50 text-primary-800 rounded-base shadow-small">
        <Layers class="w-3 h-3" />
        {totalStages} stages
      </span>
      <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-surface-50 text-primary-800 rounded-base shadow-small">
        <Clock class="w-3 h-3" />
        {formatDuration(workflow.duration_ms)}
      </span>
      <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-black border-2 {passRateBadgeClass} rounded-base shadow-small uppercase tracking-wide">
        {(workflow.pass_rate * 100).toFixed(1)}% pass rate
      </span>
      {#if workflow.failed_tasks > 0}
        <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-error-100 text-error-900 rounded-base shadow-small">
          <XCircle class="w-3 h-3" />
          {workflow.failed_tasks} failed
        </span>
      {:else}
        <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-secondary-100 text-secondary-900 rounded-base shadow-small">
          <CheckCircle2 class="w-3 h-3" />
          {workflow.passed_tasks}/{workflow.total_tasks} passed
        </span>
      {/if}

      {#if traceId && observabilityPath}
        <a
          href="{observabilityPath}?trace_id={traceId}"
          class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border-2 border-black bg-purple-100 text-purple-900 rounded-base shadow-small hover:bg-purple-200 transition-colors duration-100"
          title="Open trace in Observability"
        >
          <Activity class="w-3 h-3" />
          Trace
        </a>
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

  <!-- ─── Mobile tab switcher ──────────────────────────────────────────────── -->
  <div class="lg:hidden flex-shrink-0 border-b-2 border-black bg-surface-50">
    <div class="inline-flex w-full overflow-hidden">
      <button
        onclick={() => activePanel = 'list'}
        class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-black uppercase tracking-wide
               border-r-2 border-black transition-colors duration-100 ease-out
               {activePanel === 'list' ? 'bg-primary-800 text-white' : 'bg-surface-50 text-primary-800 hover:bg-primary-100'}"
      >
        <List class="w-3.5 h-3.5" />
        Task List
      </button>
      <button
        onclick={() => activePanel = 'detail'}
        class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-black uppercase tracking-wide
               transition-colors duration-100 ease-out
               {activePanel === 'detail' ? 'bg-primary-800 text-white' : 'bg-surface-50 text-primary-800 hover:bg-primary-100'}"
      >
        Task Detail
      </button>
    </div>
  </div>

  <!-- ─── Split-pane body ──────────────────────────────────────────────────── -->
  <div class="flex-1 min-h-0 overflow-hidden">
    {#if loading}
      <div class="flex items-center justify-center h-full p-8">
        <div class="flex flex-col items-center gap-3">
          <div class="w-10 h-10 border-2 border-black border-t-primary-500 rounded-full animate-spin"></div>
          <p class="text-xs font-black uppercase tracking-wider text-primary-700">Loading tasks…</p>
        </div>
      </div>
    {:else}
      <div class="flex h-full min-h-0">

        <!-- Left: Stage list -->
        <div class="border-r-2 border-black flex-1 overflow-hidden {activePanel === 'list' ? 'block' : 'hidden'} lg:block">
          <WorkflowStageList
            {tasks}
            executionPlan={workflow.execution_plan}
            {selectedTask}
            onTaskSelect={handleTaskSelect}
          />
        </div>

        <!-- Right: Task detail -->
        <div class="flex-1 min-w-0 overflow-hidden bg-surface-50 {activePanel === 'detail' ? 'block' : 'hidden'} lg:block">
          {#if selectedTask}
            <TaskDetailView task={selectedTask} profile={profile} {traceId} {observabilityPath} />
          {:else}
            <div class="flex flex-col items-center justify-center h-full gap-3 text-center p-8">
              <div class="w-12 h-12 border-2 border-black bg-surface-200 flex items-center justify-center rounded-base shadow-small">
                <List class="w-6 h-6 text-primary-400" />
              </div>
              <p class="text-sm font-black text-primary-500 uppercase tracking-wide">Select a task to inspect</p>
            </div>
          {/if}
        </div>

      </div>
    {/if}
  </div>

</div>
