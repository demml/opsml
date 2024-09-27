<script lang="ts">
    import { updateDriftProfile } from "$lib/scripts/monitoring/utils";
    import { type DriftConfig, type AlertConfig, type DriftProfile } from "$lib/scripts/types";
    import { createEventDispatcher } from 'svelte';

    export let showConfig = false;
    export let repository: string;
    export let name: string;
    export let version: string;
    export let driftConfig: DriftConfig;
    export let driftProfile: DriftProfile;
    const dispatch = createEventDispatcher();


    let alertConfig: AlertConfig = driftConfig.alert_config;
    let process_rule = alertConfig.alert_rule?.process?.rule;

    let zones_to_monitor: string[];

    // default to empty array
    $: zones_to_monitor = alertConfig.alert_rule?.process?.zones_to_monitor || [];


    let alert_kwargs: Record<string, any> | string;
    $: alert_kwargs =  JSON.stringify(alertConfig.alert_kwargs, null, 2);

    let dispatch_type = alertConfig.alert_dispatch_type
    let schedule = alertConfig.schedule;
    let targets = driftConfig.targets;
    let sample = driftConfig.sample;
    let sample_size = driftConfig.sample_size;

    async function handleUpdate() {

      console.log('Updating drift config');

      // check if Zone to monitor is a string
      if (typeof zones_to_monitor === 'string') {

        // cast to type string 
        let zones = zones_to_monitor as string;
        zones_to_monitor = zones.split(',');

      }

      // if alert_kwargs is a string, parse it to JSON
      if (typeof alert_kwargs === 'string') {
        alert_kwargs = JSON.parse(alert_kwargs);
      }

      // check targets 
      if (typeof targets === 'string') {
        let targetsList = targets as string;
        targets = targetsList.split(',');
      }


      let updatedDriftConfig = {
        name: name,
        repository: repository,
        version: version,
        sample: sample,
        feature_map: driftConfig.feature_map,
        sample_size: sample_size,
        targets: targets,
        alert_config: {
          dispatch_type: dispatch_type,
          schedule: schedule,
          alert_dispatch_type: dispatch_type,
          alert_rule: {
            process: {
              rule: process_rule!,
              zones_to_monitor: zones_to_monitor
            },
            percentage: undefined,
          },
          alert_kwargs: alert_kwargs as Record<string, number>
        }
      };

      showConfig = false;
      dispatch('update', { showConfig,  updatedDriftConfig});

      driftProfile.config = updatedDriftConfig;

      //serialize the updated drift profile
  
      let updated = await updateDriftProfile(name, repository, version, JSON.stringify(driftProfile, null, 2));

      if (updated.complete) {
        console.log('Drift profile updated successfully');
      } else {
        console.log('Failed to update drift profile');
      }

    }

    function handleHide() {
    showConfig = false;
    dispatch('hide', { showConfig });
  }

  </script>

<style>
  .scrollable-container {
    height: 400px; /* Adjust the height as needed */
    overflow-y: auto;
  }

</style>
  

<div class={`fixed top-10 bottom-10 right-4 h-auto rounded-2xl transition-transform duration-300 ease-in-out z-50 ${showConfig ? 'translate-x-0' : 'translate-x-full'}`}>
  <!-- Profile content goes here -->
  <section class="border-gray-100 col-span-full flex-1 items-center">
    
    <form class="z-10 mx-auto rounded-xl border-2 border-primary-500 bg-white border shadow p-4 md:w-96 md:px-5">
      <h1 class="pt-1 text-center text-lg font-bold text-primary-500">DriftConfig</h1>
      <p class="mb-1 text-gray-500 text-xs text-center">Current drift configuration using statistical process control</p>

      <div class="grid grid-cols-3 my-2 items-center gap-2">
        <div class="badge variant-soft-secondary">{repository}</div>
        <div class="badge variant-soft-secondary">{name}</div>
        <div class="badge variant-soft-secondary">{version}</div>

      </div>

      <div class="scrollable-container">
        <div class="mb-4">

          <label class="text-primary-500">Sample
            <input
              class="input rounded-lg bg-slate-200 hover:bg-slate-100"
              type="text" 
              bind:value={sample}
            />
          </label>

          <label class="text-primary-500">Sample Size
            <input
              class="input rounded-lg bg-slate-200 hover:bg-slate-100"
              type="text" 
              bind:value={sample_size}
            />
          </label>

          <label class="text-primary-500">Targets
            <input
              class="input rounded-lg bg-slate-200 hover:bg-slate-100"
              type="text" 
              bind:value={targets}
            />
          </label>

          <h2 class="py-2 text-center text-base font-bold text-primary-500">Alert Config</h2>

          <label class="text-primary-500">Dispatch Type
            <input
              class="input rounded-lg bg-slate-200 hover:bg-slate-100"
              type="text" 
              bind:value={dispatch_type}
            />
          </label>

          <label class="text-primary-500">Alert Rule
            <input
              class="input rounded-lg bg-slate-200 hover:bg-slate-100"
              type="text" 
              bind:value={process_rule}
            />
          </label>

          <label class="text-primary-500">Alert Zones
            <input
              class="input rounded-lg bg-slate-200 hover:bg-slate-100"
              type="text" 
              bind:value={zones_to_monitor}
            />
          </label>

          <label class="text-primary-500">Alert Kwargs
            <p class="mb-1 text-gray-500 text-xs">Dispatch-specific kwargs in key:value mapping</p>
            <textarea
              class="textarea rounded-lg bg-slate-200 hover:bg-slate-100"
              rows="4"
              bind:value={alert_kwargs}
              
            />
          </label>

          

          
        </div>
      </div>

      <div class="grid grid-cols-2 gap-2 py-2">
        <button type="button" class="btn bg-primary-500 text-white rounded-lg" on:click={handleHide}>
          <span>Hide</span>
        </button>
        <button type="button" class="btn bg-primary-500 text-white rounded-lg" on:click={handleUpdate}>
          <span>Update</span>
        </button>
      </div>
    </form>
  </section>
</div>