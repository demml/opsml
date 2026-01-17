<script lang="ts">
  import { X, List } from 'lucide-svelte';
  import type { GenAIEvalWorkflowResult, GenAIEvalTaskResult } from '../task';
  import Pill from '$lib/components/utils/Pill.svelte';
  import WorkflowStageList from './WorkflowStageList.svelte';
  import TaskDetailView from '../task/TaskDetailView.svelte';
  import { getServerGenAIEvalTask } from '../utils';
  import type { GenAIEvalTaskRequest } from '../types';

  let {
    workflow,
    onClose,
    showCloseButton = true,
  }: {
    workflow: GenAIEvalWorkflowResult;
    onClose?: () => void;
    showCloseButton?: boolean;
  } = $props();

  let selectedTask = $state<GenAIEvalTaskResult | null>(null);
  let tasks = $state<GenAIEvalTaskResult[]>([]);
  let showStageList = $state(true);
  let showTaskDetail = $state(true);
  let loading = $state(true);

  async function loadTasks() {
    loading = true;
    try {
      const request: GenAIEvalTaskRequest = { record_uid: workflow.record_uid };
      const response = await getServerGenAIEvalTask(fetch, request);
      tasks = response.tasks || [];

      if (tasks.length > 0) {
        selectedTask = tasks[0];
      }
      } catch (error) {
        console.error('Failed to load tasks:', error);
      } finally {
        loading = false;
      }
    }

    $effect(() => {
      loadTasks();
    });


  function handleTaskSelect(task: GenAIEvalTaskResult) {
    selectedTask = task;
    if (window.innerWidth < 1024) {
      showTaskDetail = true;
    }
  }

  function getPassRateColor(passRate: number): string {
    if (passRate >= 0.9) return 'bg-secondary-600';
    if (passRate >= 0.7) return 'bg-warning-600';
    return 'bg-error-600';
  }

  function formatDuration(durationMs: number): string {
    const seconds = durationMs / 1000;
    return seconds < 1 ? `${durationMs}ms` : `${seconds.toFixed(2)}s`;
  }

  function toggleStageList() {
    showStageList = !showStageList;
    if (!showStageList) showTaskDetail = true;
  }

  function toggleTaskDetail() {
    showTaskDetail = !showTaskDetail;
    if (!showTaskDetail) showStageList = true;
  }

  const totalStages = $derived(workflow.execution_plan.stages.length);
</script>

<div class="flex flex-col h-full bg-white">
  <div class="flex items-start justify-between p-6 border-b-2 border-black bg-surface-50 gap-6 flex-shrink-0">
    <div class="flex flex-col gap-4 flex-1 min-w-0">
      <div class="flex items-center gap-3">
        <div class={`w-2 h-10 rounded flex-shrink-0 ${getPassRateColor(workflow.pass_rate)}`}></div>
        <div class="min-w-0 flex-1">
          <h2 class="text-lg font-bold text-primary-800">Workflow Evaluation</h2>
          <p class="text-sm font-mono text-gray-600 truncate">{workflow.record_uid}</p>
        </div>
      </div>

      <div class="flex flex-wrap gap-1">
        <span class="badge text-primary-900 border-black border-1 shadow-small bg-primary-100">
          {workflow.total_tasks} tasks
        </span>
        <span class="badge text-primary-900 border-black border-1 shadow-small bg-primary-100">
          {totalStages} stages
        </span>
        <span class="badge text-primary-900 border-black border-1 shadow-small bg-primary-100">
          {formatDuration(workflow.duration_ms)}
        </span>
        <span class="badge border-black border-1 shadow-small {workflow.pass_rate >= 0.9 ? 'bg-secondary-100 text-secondary-900' : workflow.pass_rate >= 0.7 ? 'bg-warning-100 text-warning-900' : 'bg-error-100 text-error-900'}">
          {(workflow.pass_rate * 100).toFixed(1)}% pass rate
        </span>
        {#if workflow.failed_tasks > 0}
          <span class="badge text-error-900 border-black border-1 shadow-small bg-error-100">
            {workflow.failed_tasks} failed
          </span>
        {/if}
      </div>

      <div class="flex flex-wrap gap-1 text-xs">
        <Pill key="Passed" value={`${workflow.passed_tasks}/${workflow.total_tasks}`} textSize="text-xs"/>
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

  <div class="flex-1 overflow-y-auto min-h-0">
    <div class="lg:hidden flex border-b-2 border-black bg-surface-200 sticky top-0 z-10">
      <button
        onclick={toggleStageList}
        class="flex-1 py-3 text-sm font-bold transition-colors border-r-2 border-black {showStageList ? 'bg-primary-500 text-white' : 'bg-white text-primary-800'}"
      >
        <List class="w-4 h-4 inline-block mr-1" />
        Task List
      </button>
      <button
        onclick={toggleTaskDetail}
        class="flex-1 py-3 text-sm font-bold transition-colors {showTaskDetail ? 'bg-primary-500 text-white' : 'bg-white text-primary-800'}"
      >
        Task Details
      </button>
    </div>

    {#if loading}
      <div class="flex items-center justify-center h-full">
        <div class="text-center p-8">
          <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent mx-auto mb-4"></div>
          <p class="text-sm text-gray-600">Loading tasks...</p>
        </div>
      </div>
    {:else}
      <div class="flex flex-col lg:flex-row min-h-[600px] min-w-0">
        <div class="border-b-2 lg:border-b-0 lg:border-r-2 border-black lg:flex-1 {showStageList ? 'block' : 'hidden'} lg:block">
          <WorkflowStageList
            {tasks}
            executionPlan={workflow.execution_plan}
            {selectedTask}
            onTaskSelect={handleTaskSelect}
          />
        </div>

        <div class="bg-surface-50 lg:flex-1 min-w-0 {showTaskDetail ? 'block' : 'hidden'} lg:block">
          {#if selectedTask}
            <TaskDetailView task={selectedTask} allTasks={tasks} />
          {:else}
            <div class="flex items-center justify-center h-full text-gray-500 p-4 text-center">
              Select a task to view details
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>
</div>