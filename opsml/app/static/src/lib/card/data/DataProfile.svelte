<script lang="ts">
    import { type DataProfile, type FeatureProfile } from "$lib/scripts/data/types";
    import StringStatsDiv from "./StringStats.svelte";


    export let profile: DataProfile;
    export let featureNames: string[];


</script>


<div>
    {#each featureNames as name}
        {@const feature = profile.features[name]}
        <div class="pt-2 pb-10 mb-2 rounded-2xl bg-surface-50 border-2 border-primary-500 shadow-md shadow-primary-500 w-full">
          <div class="flex mb-2">
            <div>
              <header class="px-2 text-darkpurple text-lg font-bold">{feature.id}</header>
            </div>

            {#if !feature.numeric_stats}
              <div class="badge variant-soft-primary">Categorical</div>
            {:else}
              <div class="badge variant-soft-primary">Numeric</div>
            {/if}
          </div>
          {#if !feature.numeric_stats}
            {#if feature.string_stats}
              <StringStatsDiv stringStats={feature.string_stats} timestamp={feature.timestamp} />
            {/if}
          {/if}
        </div>


    {/each}

</div>