<script lang="ts">

  import { type ChartjsData, type DriftProfile, type FeatureDriftProfile, type FeatureDriftValues } from "$lib/scripts/types";
  import logo from '$lib/images/opsml-green.ico';
  import { onMount } from 'svelte';
  import TimeChartDiv from "$lib/card/run/TimeChartDiv.svelte";


  /** @type {import('./$types').LayoutData} */
  export let data;

  let driftProfile: DriftProfile;
  $: driftProfile = data.driftProfile;

  let targetFeature:FeatureDriftProfile;
  $: targetFeature = data.targetFeature;

  let features: string[];
  $: features = data.features;

  let featureValues: FeatureDriftValues;
  $: featureValues = data.featureValues;

  let driftVizData: ChartjsData;
  $: driftVizData = data.driftVizData;



  let vizId: string;
  $: vizId = "Drift values for " + targetFeature.id;

  onMount (() => {
    console.log(featureValues);
    console.log(targetFeature);
  });

</script>

{#if driftProfile}
<div class="min-h-screen">
  

  <div class="flex flex-col w-full">
    {#if driftVizData}
      <TimeChartDiv
        data={driftVizData.data}
        id={vizId}
        options={driftVizData.options}
        maxHeight={"max-h-[500px]"}
      />
    {:else}
      <div class="flex justify-center items-center h-3/5">
        <p class="text-gray-400">No feature values found for the current time period</p>
      </div>
    {/if}
  </div>

</div>
{:else}
<div class="flex min-h-screen min-h-screen flex flex-col md:grid md:space-y-0 w-full h-full md:grid-cols-12 md:flex-1 md:grid-rows-full space-y-4 md:gap-6 max-w-full max-h-full bg-white" id="notLoaded">
  <section class="pt-24 border-gray-100 col-span-full flex-1 pb-16 items-center">

    <div class="z-10 mx-auto rounded-2xl bg-slate-100 border shadow p-4 md:w-96 md:px-5">

      <img alt="OpsML logo" class="mx-auto -mt-12 mb-2 w-20" src={logo}>
      <h1 class="pt-1 text-center text-3xl font-bold text-error-500">Oops!</h1>

      <div class="mb-8 grid grid-cols-1 gap-3">
        <h2 class="text-primary-500 font-bold">No Drift Profile Detected</h2>
        <p class="mb-1 text-primary-500 text-center">
          A drift profile was not detected for this model
          If you'd like to enable monitoring, create a drift profile for this model.
        </p>

      </div>
      
    </div>
  </section>
</div>
{/if}