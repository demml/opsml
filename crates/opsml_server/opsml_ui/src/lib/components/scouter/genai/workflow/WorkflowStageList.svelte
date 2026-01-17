<script lang="ts">
  import type { GenAIEvalTaskResult, ExecutionPlan } from '../task';
  import { CheckCircle2, XCircle, GitBranch } from 'lucide-svelte';

  let {
    tasks,
    executionPlan,
    selectedTask,
    onTaskSelect,
  }: {
    tasks: GenAIEvalTaskResult[];
    executionPlan: ExecutionPlan;
    selectedTask: GenAIEvalTaskResult | null;
    onTaskSelect: (task: GenAIEvalTaskResult) => void;
  } = $props();

  const ROW_HEIGHT = 32;

  function getTaskById(taskId: string): GenAIEvalTaskResult | undefined {
    return tasks.find(t => t.task_id === taskId);
  }

  function getStatusIcon(task: GenAIEvalTaskResult) {
    if (task.condition) return GitBranch;
    return task.passed ? CheckCircle2 : XCircle;
  }

  function getStatusColor(task: GenAIEvalTaskResult): string {
    if (task.condition) return 'text-tertiary-600';
    return task.passed ? 'text-secondary-600' : 'text-error-600';
  }

  function getTaskBadgeClasses(task: GenAIEvalTaskResult): string {
    if (task.condition) {
      return 'border-tertiary-900 bg-tertiary-100 text-tertiary-900';
    }
    if (task.passed) {
      return 'border-secondary-900 bg-secondary-100 text-secondary-900';
    }
    return 'border-error-900 bg-error-100 text-error-900';
  }

  function formatDuration(startTime: string, endTime: string): string {
    const start = new Date(startTime).getTime();
    const end = new Date(endTime).getTime();
    const durationMs = end - start;
    const seconds = durationMs / 1000;
    return seconds < 1 ? `${durationMs}ms` : `${seconds.toFixed(2)}s`;
  }

  const sortedStages = $derived(
    executionPlan.stages.map((stageTaskIds, stageIndex) => {
      const stageTasks = stageTaskIds
        .map(taskId => getTaskById(taskId))
        .filter((task): task is GenAIEvalTaskResult => task !== undefined)
        .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());

      return {
        stageIndex,
        tasks: stageTasks
      };
    })
  );
</script>

<div class="flex flex-col h-full bg-white text-sm overflow-hidden">
  <div class="sticky top-0 bg-surface-50 border-b-2 border-gray-300 flex-shrink-0 px-4 py-3">
    <h3 class="text-sm font-bold text-primary-800">Execution Timeline</h3>
    <p class="text-xs text-gray-600 mt-1">{tasks.length} tasks across {executionPlan.stages.length} stages</p>
  </div>

  <div class="flex-1 overflow-auto">
    {#each sortedStages as { stageIndex, tasks: stageTasks }}
      <div class="border-b-2 border-gray-200">
        <div class="sticky top-0 bg-tertiary-100 border-b border-tertiary-300 px-4 py-2 z-10">
          <div class="flex items-center gap-2">
            <span class="flex-shrink-0 w-6 h-6 flex items-center justify-center bg-tertiary-950 text-white rounded-full text-xs font-bold">
              {stageIndex + 1}
            </span>
            <span class="text-xs font-bold text-tertiary-950">
              Stage {stageIndex + 1}
            </span>
            <span class="text-xs text-gray-600">
              ({stageTasks.length} {stageTasks.length === 1 ? 'task' : 'tasks'})
            </span>
          </div>
        </div>

        {#each stageTasks as task}
          {@const isSelected = selectedTask?.task_id === task.task_id}
          {@const StatusIcon = getStatusIcon(task)}
          {@const badgeClasses = getTaskBadgeClasses(task)}

          <button
            class="flex group cursor-pointer hover:bg-surface-100 transition-all w-full border-b border-gray-100 relative"
            style="height: {ROW_HEIGHT}px"
            class:bg-primary-50={isSelected}
            onclick={() => onTaskSelect(task)}
          >
            <div class={`absolute left-0 top-0 bottom-0 w-1 ${getStatusColor(task).replace('text-', 'bg-')}`}></div>

            <div class="flex items-center gap-3 px-4 pl-6 w-full overflow-hidden">
              <StatusIcon class="w-4 h-4 flex-shrink-0 {getStatusColor(task)}" />

              <span class="text-xs truncate text-gray-900 flex-1 min-w-0 text-left {isSelected ? 'font-bold' : 'font-medium'}" title={task.task_id}>
                {task.task_id}
              </span>

              {#if !task.passed && !task.condition}
                <span class="text-[10px] bg-error-100 text-error-800 px-1.5 rounded font-bold uppercase tracking-wider">Fail</span>
              {/if}

              <span class="w-16 text-[10px] font-mono text-gray-500 text-right flex-shrink-0">
                {formatDuration(task.start_time, task.end_time)}
              </span>
            </div>
          </button>
        {/each}
      </div>
    {/each}
  </div>
</div>