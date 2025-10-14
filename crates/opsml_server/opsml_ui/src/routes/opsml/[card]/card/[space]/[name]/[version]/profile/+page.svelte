<script lang="ts">
  import DataProfileViz from "$lib/components/card/data/DataProfileViz.svelte";
  import type {DataProfile} from "$lib/components/card/data/types";
  import type { PageProps } from './$types';

  let { data }: PageProps = $props();

  let dataProfile: DataProfile | undefined = $state(data.dataProfile);
  let featureNames: string[] = $state(data.featureNames);

 
</script>


{#if dataProfile}
  <div class="grid grid-cols-12 gap-4 px-4 pt-4">
    <div class="flex-1 pb-10"> 
      <DataProfileViz
        features={featureNames}
        profile={dataProfile}
      />
    </div>
  </div>

{:else}
  <div class="col-span-12 flex items-center justify-center px-4">
    <section class="pt-4 border-gray-100 col-span-full flex-1 pb-16 md:pb-0 items-center">
      <div class="z-10 mx-auto rounded-2xl bg-surface-50 border-black border-2 shadow p-4 md:w-96 md:px-5">
        <h1 class="pt-1 text-center text-lg font-bold text-primary-800">Data Profile</h1>
        <p class="mb-6 text-center text-surface-950 text-smd">
          No data profile is available for this card.
        </p>
      </div>
    </section>
  </div>
{/if}
