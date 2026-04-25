<script lang="ts">
  import { isAssertionTask, type AnyTask } from '../task';
  import { ClipboardList, GitBranch, Brain, Layers } from 'lucide-svelte';

  let { task }: { task: AnyTask } = $props();


  const taskTypeLabel: Record<string, string> = {
    Assertion: 'Assertion',
    LLMJudge: 'LLM Judge',
    TraceAssertion: 'Trace Assertion',
    AgentAssertion: 'Agent Assertion',
    Conditional: 'Conditional',
    HumanValidation: 'Human Validation',
  };

  const taskTypeColor: Record<string, string> = {
    Assertion: 'bg-primary-100 text-primary-900 border-primary-800',
    LLMJudge: 'bg-secondary-100 text-secondary-900 border-secondary-800',
    TraceAssertion: 'bg-tertiary-100 text-tertiary-900 border-tertiary-800',
    AgentAssertion: 'bg-warning-100 text-warning-900 border-warning-800',
    Conditional: 'bg-warning-100 text-warning-900 border-warning-800',
    HumanValidation: 'bg-error-100 text-error-800 border-error-800',
  };

  const taskTypeIcon: Record<string, typeof ClipboardList> = {
    Assertion: ClipboardList,
    LLMJudge: Brain,
    TraceAssertion: Layers,
    AgentAssertion: Brain,
    Conditional: GitBranch,
    HumanValidation: ClipboardList,
  };

  const label = $derived(taskTypeLabel[task.task_type] ?? task.task_type);
  const colorClass = $derived(taskTypeColor[task.task_type] ?? 'bg-surface-200 text-black border-black');
  const Icon = $derived(taskTypeIcon[task.task_type] ?? ClipboardList);

  /** context_path for Assertion/LLMJudge, stringified assertion for TraceAssertion */
  const fieldDisplay = $derived.by(() => {
    if ('context_path' in task) return task.context_path ?? '—';
    if ('assertion' in task) {
      const key = Object.keys(task.assertion)[0];
      return key ?? '—';
    }
    return '—';
  });

  const expectedDisplay = $derived(
    task.expected_value !== null && task.expected_value !== undefined
      ? JSON.stringify(task.expected_value, null, 2)
      : 'null'
  );

  const dependsOnDisplay = $derived(
    task.depends_on.length > 0 ? task.depends_on.join(', ') : '—'
  );
</script>

<article class="flex min-w-0 w-full flex-col border-2 border-black shadow-small bg-surface-100 overflow-hidden">
  <!-- Card Header -->
   <header class = "flex flex-col min-w-0 px-3 py-2 border-b-2 border-black bg-primary-500">
    <div class="flex justify-between items-center min-w-0 gap-2 mb-0.5">
      <span class="text-[10px] font-black uppercase tracking-widest text-white mb-0.5">Task ID</span>
      <span class="badge text-[9px] border-1 px-1.5 rounded-full flex-shrink-0 whitespace-nowrap {colorClass}">
        <Icon class="w-3 h-3 inline-block mr-1 -mt-px" />
        {label}
      </span>
    </div>
    <div class="relative group">
      <p class="text-[13px] font-mono font-bold text-white truncate cursor-help min-w-0" title={task.id}>{task.id}</p>
      <div class="absolute left-0 top-full mt-2 px-3 py-2 bg-slate-900 text-white text-xs font-mono rounded-lg border-2 border-white shadow-[4px_4px_0px_0px_rgba(255,255,255,0.3)] opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 max-w-sm break-all">
        {task.id}
        <div class="absolute -top-1 left-4 w-2 h-2 bg-slate-900 border-t-2 border-l-2 border-white transform rotate-45"></div>
      </div>
    </div>
  </header>

  <!-- Card Body -->
  <div class="flex flex-col gap-2 px-3 py-2.5 text-[11px]">

    <div class="flex flex-col gap-0.5">
      <span class="text-[10px] font-black uppercase tracking-wider text-slate-500">Context Path</span>
        <span class="font-mono text-slate-700 truncate min-w-0" title={fieldDisplay}>{fieldDisplay}</span>
    </div>

    {#if isAssertionTask(task) && task.item_context_path}
      <div class="flex flex-col gap-0.5">
        <span class="text-[10px] font-black uppercase tracking-wider text-slate-500">Item Context Path</span>
        <span class="font-mono text-slate-700 truncate" title={task.item_context_path}>{task.item_context_path}</span>
      </div>
    {/if}

    <div class="flex items-center gap-2.5">
      <div class="flex flex-col gap-0.5 flex-1">
        <span class="text-[10px] font-black uppercase tracking-wider text-slate-500">Operator</span>
        <span class="font-mono text-primary-800 truncate min-w-0">{task.operator}</span>
      </div>
      <div class="flex flex-col gap-0.5 flex-1">
        <span class="text-[10px] font-black uppercase tracking-wider text-slate-500">Condition</span>
        <span class="font-bold {task.condition ? 'text-secondary-700' : 'text-error-600'}">{task.condition ? 'True' : 'False'}</span>
      </div>
    </div>

    <div class="flex flex-col gap-0.5">
      <span class="text-[10px] font-black uppercase tracking-wider text-slate-500">Expected Value</span>
      <pre class="bg-slate-700 text-secondary-300 rounded-md px-2 py-1 text-[10px] font-mono overflow-x-auto whitespace-pre-wrap break-all max-h-16 max-w-full">{expectedDisplay}</pre>
    </div>

    {#if task.description}
      <div class="flex flex-col gap-0.5">
        <span class="text-[10px] font-black uppercase tracking-wider text-slate-500">Description</span>
        <p class="text-slate-600 font-mono leading-snug break-words line-clamp-2">{task.description}</p>
      </div>
    {/if}

    <div class="flex flex-col gap-0.5">
      <span class="text-[10px] font-black uppercase tracking-wider text-slate-500">Depends On</span>
      <span class="font-mono text-slate-600 truncate min-w-0" title={dependsOnDisplay}>{dependsOnDisplay}</span>
    </div>

  </div>
</article>
