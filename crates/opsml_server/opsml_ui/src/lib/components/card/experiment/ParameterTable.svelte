<script lang="ts">

  import type { Parameter, ParameterValue } from "../card_interfaces/experimentcard";
  import { Cog } from 'lucide-svelte';
  
  let { 
      parameters,
      open,
      setOpen
    } = $props<{
      parameters: Parameter[];
      open: boolean;
      setOpen: (open: boolean) => void;
    }>();
  
  function getParameterValue(paramValue: ParameterValue): string | number {
    if ('Int' in paramValue) return paramValue.Int;
    if ('Float' in paramValue) return paramValue.Float;
    if ('Str' in paramValue) return paramValue.Str;
    return '';
  }
  
  </script>
  
{#if open}
  <div class="flex flex-col gap-4">
    <div class="flex flex-row justify-between">
      <div class="flex flex-row">
        <div class="self-center" aria-label="Time Interval">
          <Cog color="#8059b6"/>
        </div>
        <header class="pl-2 text-primary-800 self-center font-bold">Parameters</header>
      </div>
      <button type="button" class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2 self-center" onclick={() => setOpen(false)}>Close</button>
    </div>
    {#if parameters.length === 0}
    <div class="h-full border-2 border-black flex items-center justify-center">
      <div class="text-center text-gray-500 text-primary-500 font-bold">
        No alerts to display
      </div>
    </div>
    {:else}
    <div class="h-full overflow-auto rounded-lg border-2 border-black">
      <table class="w-full text-black text-sm md:text-base bg-slate-100">
        <thead class="bg-primary-500 sticky top-0">
          <tr>
            <th class="text-black pl-4 py-2 text-center">Name</th>
            <th class="text-black pr-4 py-2 text-center">Value</th>
          </tr>
        </thead>
        <tbody>
          {#each parameters as parameter}
          <tr class="border-t hover:bg-primary-300 py-2">
            <td class="p-2 text-sm text-center">{parameter.name}</td>
            <td class="p-2 text-sm text-center">{getParameterValue(parameter.value)}</td>
          </tr>
        {/each}
        </tbody>
      </table>
    </div>
    {/if}
  </div>
{:else}
  <div class="flex flex-row justify-between justify-between">
    <div class="flex flex-row">
      <div class="self-center" aria-label="Time Interval">
        <Cog color="#8059b6"/>
      </div>
      <header class="pl-2 text-primary-800 self-center font-bold">Parameters</header>
    </div>
    <button type="button" class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2 self-center" onclick={() =>setOpen(true)}>Open</button>
  </div>
{/if}
    