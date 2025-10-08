<script lang="ts">
  //import type { UiHardwareMetrics } from '$lib/components/card/experiment/types';
  import type { PageProps } from './$types';
  let { data }: PageProps = $props();
  import FigureViz from '$lib/components/card/experiment/FigureViz.svelte';

  let figures = data.figures;

  

</script>

<div class="flex-1 mx-auto w-10/12 pb-10 flex justify-center px-4">
  <div class="w-full overflow-auto">
    {#if figures && figures.length > 0}
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 w-full p-4">
        {#each figures as figure}
          <FigureViz {figure} />
        {/each}
      </div>
    {:else}
      <div class="text-center py-4 text-primary-800">
        <p>No figures available for this experiment</p>
      </div>
    {/if}
  </div>
</div>




