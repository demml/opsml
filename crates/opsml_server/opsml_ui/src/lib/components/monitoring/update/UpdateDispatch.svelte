<script lang="ts">
  import { Modal } from '@skeletonlabs/skeleton-svelte';
  import { AlertDispatchType, type AlertDispatchConfig } from '../types';
  import type { DriftConfigType } from '../util';
  import Dropdown from '$lib/components/utils/Dropdown.svelte';
  import { z } from 'zod';


  
    const slackSchema = z.object({
      channel: z.string(),
    });

    const opsGenieSchema = z.object({
      team: z.string(),
      priority: z.union([
            z.literal('p1'),
            z.literal('p2'),
            z.literal('p3'),
            z.literal('p4'),
            z.literal('p5'),
        ])
    });
  
    type SlackConfigSchema = z.infer<typeof slackSchema>;
    type OpsGenieConfigSchema = z.infer<typeof opsGenieSchema>;
  
    let { 
      dispatchConfig= $bindable(),
    } = $props<{
      dispatchConfig: AlertDispatchConfig
    }>();
    
      
    // set dispatch type to whatever is not None (can be slack or opsgenie)
    let dispatchType = $state<AlertDispatchType>(
      dispatchConfig.Slack ? AlertDispatchType.Slack : AlertDispatchType.OpsGenie
    );
    let dispatchOptions = $state(Object.values(AlertDispatchType));

    let slackChannel = $state(dispatchConfig?.Slack?.channel ?? '');
    let opsGenieTeam = $state(dispatchConfig?.OpsGenie?.team ?? '');
    let opsGeniePriority = $state(dispatchConfig?.OpsGenie?.priority ?? '');

    let slackErrors = $state<Partial<Record<keyof SlackConfigSchema, string>>>({});
    let opsGenieErrors = $state<Partial<Record<keyof OpsGenieConfigSchema, string>>>({});
  
   

    function validateSlackForm(): boolean {
  
      try {
        slackSchema.parse({
          channel: slackChannel
        });
  
        slackErrors = {};
  
        dispatchConfig.Slack = {
          channel: slackChannel
        };
        return true;
  
      } catch (error) {
  
        if (error instanceof z.ZodError) {
          slackErrors = error.errors.reduce((acc, curr) => {
            const path = curr.path[0] as keyof SlackConfigSchema;
            acc[path] = curr.message;
            return acc;
          }, {} as Record<keyof SlackConfigSchema, string>);
        }
        return false;
      }
    }

    function validateOpsGenieForm(): boolean {
  
      try {
        opsGenieSchema.parse({
          team: opsGenieTeam,
          priority: opsGeniePriority
        });
  
        opsGenieErrors = {};
  
        dispatchConfig.OpsGenie = {
          team: opsGenieTeam,
          priority: opsGeniePriority
        };
        return true;
  
      } catch (error) {
  
        if (error instanceof z.ZodError) {
          opsGenieErrors = error.errors.reduce((acc, curr) => {
            const path = curr.path[0] as keyof OpsGenieConfigSchema;
            acc[path] = curr.message;
            return acc;
          }, {} as Record<keyof OpsGenieConfigSchema, string>);
        }
        return false;
      }
    }

  </script>
    
<div class="flex flex-col overflow-auto min-h-full">
  <div class="flex flex-col pb-2 justify-between">
    <header class="pl-2 text-xl font-bold text-primary-800">Update Dispatch</header> 
    <Dropdown 
          bind:selectedValue={dispatchType}
          bind:values={dispatchOptions}
    />
  </div>
  <div class="grid grid-cols-1 gap-3">

    {#if dispatchType === AlertDispatchType.Slack}
      <label class="text-surface-950">
        Slack Channel
        <input
          class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
          type="text" 
          placeholder={slackChannel}
          bind:value={slackChannel}
        />
        {#if slackErrors.channel}
          <span class="text-red-500 text-sm">{slackErrors.channel}</span>
        {/if}
      </label>
    {/if}

    {#if dispatchType === AlertDispatchType.OpsGenie}
      <label class="text-surface-950">
        OpsGenie Team
        <input
          class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
          type="text" 
          placeholder={opsGenieTeam}
          bind:value={opsGenieTeam}
        />
        {#if opsGenieErrors.team}
          <span class="text-red-500 text-sm">{opsGenieErrors.team}</span>
        {/if}
      </label>

      <label class="text-surface-950">
        OpsGenie Priority
        <input
          class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
          type="text" 
          placeholder={opsGeniePriority}
          bind:value={opsGeniePriority}
        />
        {#if opsGenieErrors.priority}
          <span class="text-red-500 text-sm">{opsGenieErrors.priority}</span>
        {/if}
      </label>
      
    {/if}
  </div>
</div>



  

    
    
    