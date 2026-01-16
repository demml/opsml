<script lang="ts">
  import type { GenAIEvalTaskResult, ExecutionPlan } from '../task';
  import { CheckCircle2, XCircle, Clock } from 'lucide-svelte';

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

  function getStatusIcon(passed: boolean) {
    return passed ? CheckCircle2 : XCircle;
  }

  function getStatusColor(passed: boolean): string {
    return passed ? 'text-success-600' : 'text-error-600';
  }

  function getTaskBadgeClasses(task: GenAIEvalTaskResult): string {
    if (task.passed) {
      return 'border-success-950 bg-success-100 text-success-950';
    }
    return 'border-error-800 bg-error-100 text-error-800';
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
          {@const StatusIcon = getStatusIcon(task.passed)}
          {@const badgeClasses = getTaskBadgeClasses(task)}

          <button
            class="flex group cursor-pointer hover:bg-surface-600 transition-colors w-full"
            style="height: {ROW_HEIGHT}px"
            class:bg-primary-50={isSelected}
            onclick={() => onTaskSelect(task)}
            onkeydown={(e) => e.key === 'Enter' && onTaskSelect(task)}
            tabindex="0"
          >
            <div class="flex items-center gap-2 px-4 w-full overflow-hidden">
              <StatusIcon class="w-4 h-4 flex-shrink-0 {getStatusColor(task.passed)}" />

              <span class="border px-1.5 py-0.5 text-xs rounded flex-shrink-0 {badgeClasses}">
                {task.task_type}
              </span>

              <span class="text-xs truncate font-medium text-gray-900 flex-1 min-w-0 text-left" title={task.task_id}>
                {task.task_id}
              </span>

              <span class="w-16 text-xs font-mono text-gray-600 text-right flex-shrink-0 whitespace-nowrap">
                {formatDuration(task.start_time, task.end_time)}
              </span>
            </div>
          </button>
        {/each}
      </div>
    {/each}
  </div>
</div>