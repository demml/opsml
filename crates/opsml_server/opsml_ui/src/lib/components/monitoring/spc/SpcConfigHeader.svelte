<script lang="ts">
  import { hasConsoleConfig, hasOpsGenieConfig, hasSlackConfig } from "../types";
  import type { SpcAlertConfig, SpcDriftConfig } from "./spc";
  import Pill from "../../utils/Pill.svelte";
  import UpdateModal from "../update/UpdateModal.svelte";
  import type { DriftProfile } from "../util";
;

  // props
  let { 
    config,
    alertConfig,
    profile,
  } = $props<{
    config: SpcDriftConfig;
    alertConfig: SpcAlertConfig;
    profile: DriftProfile;
  }>();

  
  </script>

<div class="grid grid-cols-1 gap-2 w-full h-auto">
  <div class="flex flex-row gap-2">
    <div class="items-center text-lg mr-2 font-bold text-primary-800">Config:</div>
    <Pill key="Schedule" value={alertConfig.schedule} />
    <Pill key="Rule" value={alertConfig.rule} />
    {#if config.sample}
      <Pill key="Sample size" value={config.sample_size} />
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
    <UpdateModal 
      config={config} 
      driftType={config.drift_type}
      profile={profile}
      />
  </div>
</div>