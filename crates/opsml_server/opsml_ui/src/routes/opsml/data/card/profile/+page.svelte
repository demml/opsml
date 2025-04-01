<script lang="ts">
  import DataProfileViz from "$lib/components/card/data/DataProfileViz.svelte";
  import { Accordion } from '@skeletonlabs/skeleton-svelte';
  import { CirclePlus, Plus, Minus } from 'lucide-svelte';
  import type {DataProfile} from "$lib/components/card/data/types";
  let { data }: PageProps = $props();

  let dataProfile: DataProfile | undefined = $state(data.dataProfile);
  let featureNames: string[] = $state(data.featureNames);

</script>

<div class="flex-1 mx-auto w-9/12 pb-10 flex justify-center overflow-auto px-4">
  {#if dataProfile}
      <DataProfileViz
        features={featureNames}
        profile={dataProfile}
      />
  {:else}
  <div class="h-64 w-96 z-10 mx-auto rounded-2xl bg-slate-100 border shadow p-4 flex flex-col justify-center items-center">
    <h1 class="pt-1 text-center text-3xl font-bold text-primary-800">No Data Profile Found!</h1>
    <div class="mb-8 grid grid-cols-1 gap-3">
      <p class="mb-1 text-black text-center overflow-x-scroll">A data profile was not saved with the current DataCard</p>
    </div>
  </div>
  {/if}
</div>