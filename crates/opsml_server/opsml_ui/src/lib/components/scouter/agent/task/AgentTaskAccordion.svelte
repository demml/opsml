<script lang="ts">
  import { Accordion } from '@skeletonlabs/skeleton-svelte';
  import type { AssertionTasks } from '../types';
  import type { AnyTask } from '../task';
  import AgentTaskCard from './AgentTaskCard.svelte';
  import { ListChecks} from 'lucide-svelte';

  let { tasks }: { tasks: AssertionTasks } = $props();

  const allTasks = $derived<AnyTask[]>([
    ...tasks.assertion,
    ...tasks.judge,
    ...tasks.trace,
  ]);

  const totalCount = $derived(allTasks.length);
  const hasAnyTasks = $derived(totalCount > 0);

  const breakdownLabel = $derived(() => {
    const parts: string[] = [];
    if (tasks.assertion.length) parts.push(`${tasks.assertion.length} Assertion`);
    if (tasks.judge.length) parts.push(`${tasks.judge.length} LLM Judge`);
    if (tasks.trace.length) parts.push(`${tasks.trace.length} Trace`);
    return parts.join(' · ');
  });
</script>

{#if hasAnyTasks}
  <div class="bg-white border-2 border-black rounded-xl shadow overflow-hidden">
    <Accordion collapsible>
      <Accordion.Item
        value="tasks"
        controlBase="bg-secondary-200 w-full flex items-center justify-between px-5 py-3.5 border-b-2 border-black cursor-pointer transition-opacity hover:bg-slate-100 text-primary-800 hover:text-primary-800"
        panelBase="p-0"
        spaceY=""
      >
        {#snippet control()}
          <div class="flex items-center gap-3">
            <ListChecks class="w-5 h-5 text-primary-950 flex-shrink-0" />
            <div class="flex flex-col items-start">
              <span class="font-black text-base uppercase tracking-tight text-primary-800">Evaluation Tasks</span>
              <span class="text-[10px] font-mono text-primary-800">{breakdownLabel()}</span>
            </div>
          </div>
        {/snippet}

        {#snippet panel()}
          <div class="overflow-x-auto bg-white border-black">
            <div class="flex gap-3 p-4 w-max min-w-full">
              {#each allTasks as task (task.id)}
                <AgentTaskCard {task} />
              {/each}
            </div>
          </div>
        {/snippet}
      </Accordion.Item>
    </Accordion>
  </div>
{/if}
