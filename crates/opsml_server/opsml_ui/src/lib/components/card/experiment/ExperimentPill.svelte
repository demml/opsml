<script lang="ts">
  import type { Experiment } from "./types";

 
    let { 
       experiment,
       active,
       setActive
     } = $props<{
        experiment: Experiment; 
        active: boolean;
        setActive: (experiment: Experiment) => void;
     }>();
  
  </script>
  
{#if active}
  <label class="flex items-center space-x-2">
    <input class="checkbox bg-primary-500 h-5 w-5 border-1 border-black rounded-none" type="checkbox" checked onchange={() => setActive(experiment)}/>
    <p class="text-black">{experiment.version}</p>
  </label>
{:else}
<label class="flex items-center space-x-2">
  <input class="checkbox h-5 w-5 bg-white h-5 w-5 border-1 border-black rounded-none" type="checkbox" onchange={() => setActive(experiment)}/>
  <p class="text-black">{experiment.version}</p>
</label>
{/if}
