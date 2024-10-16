<script lang="ts">
    import { type DataProfile, type FeatureProfile } from "$lib/scripts/data/types";
    import StringStatsDiv from "./StringStats.svelte";
    import { Accordion, AccordionItem } from '@skeletonlabs/skeleton';

    export let profile: DataProfile;
    export let featureNames: string[];


</script>


<div>
  <Accordion>
    {#each featureNames as name}
        {@const feature = profile.features[name]}

        <AccordionItem class="bg-surface-50 rounded-lg border border-2 border-primary-500">
          <svelte:fragment slot="summary">
            <div class="flex mb-1">
              <div>
                <header class="px-2 text-darkpurple text-lg font-bold">{feature.id}</header>
              </div>

              {#if !feature.numeric_stats}
                <div class="badge variant-soft-primary">Categorical</div>
              {:else}
                <div class="badge variant-soft-primary">Numeric</div>
              {/if}
            </div>
          </svelte:fragment>

          <svelte:fragment slot="content">
       
          <div class="min-h-40 max-h-48 mb-5">
            {#if !feature.numeric_stats}
              {#if feature.string_stats}
                <StringStatsDiv stringStats={feature.string_stats} timestamp={feature.timestamp} name={name} />
              {/if}
            {/if}
          </div>
        

          </svelte:fragment>
        </AccordionItem>


    {/each}
  </Accordion>

</div>