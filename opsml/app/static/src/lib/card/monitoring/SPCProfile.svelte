<script lang="ts">
    import { type DriftConfig, type AlertConfig } from "$lib/scripts/types";

    export let showProfile = false;
    export let repository: string;
    export let name: string;
    export let version: string;
    export let driftConfig: DriftConfig;


    let alertConfig: AlertConfig = driftConfig.alert_config;
    let process_rule = alertConfig.alert_rule?.process?.rule;

    let zones_to_monitor: string[];

    // default to empty array
    $: zones_to_monitor = alertConfig.alert_rule?.process?.zones_to_monitor || [];


    let alert_kwargs: Record<string, any> | string;
    $: alert_kwargs =  alertConfig.alert_kwargs;

    let dispatch_type = alertConfig.alert_dispatch_type
    let targets = driftConfig.targets;
    let sample = driftConfig.sample;
    let sample_size = driftConfig.sample_size;

    async function handleUpdate() {

      // check if Zone to monitor is a string
      if (typeof zones_to_monitor === 'string') {

        // cast to type string 
        let zones = zones_to_monitor as string;
        zones_to_monitor = zones.split(',');

      }

      // check if Alert Kwargs is an empty string
      if (typeof alert_kwargs === 'string' && alert_kwargs === '') {
        alert_kwargs = {};
      } else {
        alert_kwargs = JSON.parse(alert_kwargs as string);
        console.log(alert_kwargs);
      }
    

      let updatedDriftConfig = {
        sample: sample,
        sample_size: sample_size,
        targets: targets,
        alert_config: {
          alert_dispatch_type: dispatch_type,
          alert_rule: {
            process: {
              rule: process_rule,
              zones_to_monitor: zones_to_monitor
            }
          },
          alert_kwargs: alert_kwargs
        }
      }

      console.log(updatedDriftConfig);

    }
  </script>

<style>
  .scrollable-container {
    height: 400px; /* Adjust the height as needed */
    overflow-y: auto;
  }

</style>
  

<div class={`fixed top-10 bottom-10 right-4 h-auto rounded-2xl transition-transform duration-300 ease-in-out z-50 ${showProfile ? 'translate-x-0' : 'translate-x-full'}`}>
  <!-- Profile content goes here -->
  <section class="border-gray-100 col-span-full flex-1 items-center">
    
    <form class="z-10 mx-auto rounded-xl border-2 border-primary-500 bg-slate-100 border shadow p-4 md:w-96 md:px-5" on:submit|preventDefault={handleUpdate}>
      <h1 class="pt-1 text-center text-lg font-bold text-primary-500">DriftConfig</h1>
      <p class="mb-1 text-gray-500 text-xs text-center">Current drift configuration using statistical process control</p>

      <div class="grid grid-cols-3 my-2 items-center gap-2">
        <div class="badge variant-soft-primary">{repository}</div>
        <div class="badge variant-soft-primary">{name}</div>
        <div class="badge variant-soft-primary">{version}</div>

      </div>

      <div class="scrollable-container">
        <div class="mb-4">

          <p class="mb-1 text-gray-500 text-xs text-center">Drift Config</p>

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
              class="input rounded-lg bg-slate-200 hover:bg-slate-100"
              rows="4"
              bind:value={alert_kwargs}
            ></textarea>
          </label>

          

          
        </div>
      </div>

      <div class="grid justify-items-center">
        <button type="submit" class="btn bg-primary-500 text-white rounded-lg md:w-72 justify-self-center mb-2">
          <span>Update</span>
        </button>
      </div>
    </form>
  </section>
</div>