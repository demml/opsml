<script lang="ts">
    import { AlertDispatchType, DriftType, hasConsoleConfig, hasOpsGenieConfig, hasSlackConfig } from "./types";
    import { getProfileConfig, getProfileFeatures, type DriftProfile, type DriftProfileResponse } from "./util";
    import { Clock } from 'lucide-svelte';
    import { TimeInterval } from '$lib/components/monitoring/types';
    import Dropdown from '$lib/components/utils/Dropdown.svelte';
    import { KeySquare } from 'lucide-svelte';
    import type { CustomMetricAlertConfig, CustomMetricDriftConfig } from "./custom";
    import Pill from "../utils/Pill.svelte";
    import UpdateConfigModal from "./UpdatecConfigModal.svelte";
  
    // props
    let { 
      config,
      alertConfig,
    } = $props<{
      config: CustomMetricDriftConfig;
      alertConfig: CustomMetricAlertConfig;
    }>();

  </script>

<div class="grid grid-cols-1 gap-2 w-full h-auto">
  <div class="flex flex-row gap-2">
    <div class="items-center text-lg mr-2 font-bold text-primary-800">Config:</div>
    <Pill key="Schedule" value={alertConfig.schedule} />
    {#if config.sample}
      <Pill key="Sample" value={config.sample_size} />
    {/if}
   
  </div>

  <div class="flex flex-row gap-2">

    <div class="items-center text-lg mr-2 font-bold text-primary-800">Dispatch:</div>
    
    {#if hasSlackConfig(alertConfig.dispatch_config)}
      <Pill key="Slack Channel" value={alertConfig.dispatch_config.Slack.channel} />
    {/if}

    {#if hasOpsGenieConfig(alertConfig.dispatch_config)}
      <Pill key="OpsGenie Team" value={alertConfig.dispatch_config.OpsGenie.team} />
      <Pill key="OpsGenie Priority" value={alertConfig.dispatch_config.OpsGenie.priority} />
    {/if}

    {#if hasConsoleConfig(alertConfig.dispatch_config)}
      <Pill key="Console" value= {alertConfig.dispatch_config.Console.enabled} />
    {/if}
  </div>
  <div class="flex flex-row justify-end gap-2">

    <UpdateConfigModal/>

  </div>
</div>