<script lang="ts">
  import type { EvalTaskResult, ExecutionPlan } from '../task';
  import { CheckCircle2, XCircle, GitBranch } from 'lucide-svelte';

  let {
    tasks,
    executionPlan,
    selectedTask,
    onTaskSelect,
  }: {
    tasks: EvalTaskResult[];
    executionPlan: ExecutionPlan;
    selectedTask: EvalTaskResult | null;
    onTaskSelect: (task: EvalTaskResult) => void;
  } = $props();

  function getTaskById(taskId: string): EvalTaskResult | undefined {
    return tasks.find(t => t.task_id === taskId);
  }

  function getStatusIcon(task: EvalTaskResult) {
    if (task.condition) return GitBranch;
    return task.passed ? CheckCircle2 : XCircle;
  }

  function getStatusBarColor(task: EvalTaskResult): string {
    if (task.condition) return 'bg-tertiary-500';
    return task.passed ? 'bg-secondary-500' : 'bg-error-600';
  }

  function getStatusIconColor(task: EvalTaskResult): string {
    if (task.condition) return 'text-tertiary-600';
    return task.passed ? 'text-secondary-600' : 'text-error-600';
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
        .filter((task): task is EvalTaskResult => task !== undefined)
        .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());
      return { stageIndex, tasks: stageTasks };
    })
  );
</script>

<div class="flex flex-col h-full bg-surface-50 overflow-hidden text-sm">

  <!-- Section header -->
  <div class="flex-shrink-0 sticky top-0 z-10 bg-surface-50 border-b-2 border-black px-4 py-2.5">
    <h3 class="text-xs font-black uppercase tracking-wider text-primary-950">Execution Timeline</h3>
    <p class="text-xs font-mono text-primary-700 mt-0.5">
      {tasks.length} tasks across {executionPlan.stages.length} stages
    </p>
  </div>

  <div class="flex-1 overflow-auto">
    {#each sortedStages as { stageIndex, tasks: stageTasks }}

      <!-- Stage group -->
      <div class="border-b border-black/10">

        <!-- Stage header: sticky top-0 because section header is outside the scroll container -->
        <div class="sticky top-0 z-[5] bg-primary-50 border-b border-black/20 px-4 py-1.5">
          <div class="flex items-center gap-2">
            <span class="flex-shrink-0 w-5 h-5 flex items-center justify-center bg-primary-800 text-white rounded-base text-[10px] font-black shadow-small">
              {stageIndex + 1}
            </span>
            <span class="text-xs font-black uppercase tracking-wider text-primary-950">
              Stage {stageIndex + 1}
            </span>
            <span class="text-xs font-mono text-primary-700">
              ({stageTasks.length} {stageTasks.length === 1 ? 'task' : 'tasks'})
            </span>
          </div>
        </div>

        <!-- Task rows -->
        {#each stageTasks as task}
          {@const isSelected = selectedTask?.task_id === task.task_id}
          {@const StatusIcon = getStatusIcon(task)}

          <button
            class="relative flex items-center gap-3 px-4 pl-5 w-full h-9 border-b border-black/10
                   transition-colors duration-100 ease-out text-left
                   {isSelected ? 'bg-primary-100' : 'bg-surface-50 hover:bg-primary-50'}"
            onclick={() => onTaskSelect(task)}
          >
            <!-- Left status bar -->
            <div class="absolute left-0 top-0 bottom-0 w-1 {getStatusBarColor(task)}"></div>

            <!-- Status icon -->
            <StatusIcon class="w-3.5 h-3.5 flex-shrink-0 {getStatusIconColor(task)}" />

            <!-- Task name -->
            <span
              class="flex-1 text-xs truncate text-primary-950 min-w-0 {isSelected ? 'font-bold' : 'font-medium'}"
              title={task.task_id}
            >
              {task.task_id}
            </span>

            <!-- Fail badge -->
            {#if !task.passed && !task.condition}
              <span class="flex-shrink-0 text-[10px] font-black uppercase tracking-wider px-1.5 py-0.5 bg-error-100 text-error-900 border border-black rounded-base shadow-small">
                Fail
              </span>
            {/if}

            <!-- Duration -->
            <span class="flex-shrink-0 w-14 text-[10px] font-mono text-primary-700 text-right">
              {formatDuration(task.start_time, task.end_time)}
            </span>
          </button>

        {/each}
      </div>

    {/each}
  </div>

</div>
