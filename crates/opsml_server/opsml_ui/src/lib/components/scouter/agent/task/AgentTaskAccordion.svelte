<script lang="ts">
  import { Accordion } from '@skeletonlabs/skeleton-svelte';
  import type { AssertionTasks } from '../types';
  import type { AnyTask } from '../task';
  import AgentTaskCard from './AgentTaskCard.svelte';
  import { ListChecks} from 'lucide-svelte';

  let { tasks }: { tasks: AssertionTasks } = $props();

  const assertionTasks = $derived(tasks.assertion ?? []);
  const judgeTasks = $derived(tasks.judge ?? []);
  const traceTasks = $derived(tasks.trace ?? []);
  const agentTasks = $derived(tasks.agent ?? []);

  const allTasks = $derived<AnyTask[]>([
    ...assertionTasks,
    ...judgeTasks,
    ...traceTasks,
    ...agentTasks,
  ]);

  const totalCount = $derived(allTasks.length);
  const hasAnyTasks = $derived(totalCount > 0);

  const breakdownLabel = $derived(() => {
    const parts: string[] = [];
    if (assertionTasks.length) parts.push(`${assertionTasks.length} Assertion`);
    if (judgeTasks.length) parts.push(`${judgeTasks.length} LLM Judge`);
    if (traceTasks.length) parts.push(`${traceTasks.length} Trace`);
    if (agentTasks.length) parts.push(`${agentTasks.length} Agent`);
    return parts.join(' · ');
  });
</script>

{#if hasAnyTasks}
  <div class="bg-white border-2 border-black rounded-base shadow overflow-hidden">
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
          <div class="bg-white border-black overflow-hidden">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 p-3">
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
