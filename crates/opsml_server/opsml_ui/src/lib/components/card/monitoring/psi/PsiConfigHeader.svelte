<script lang="ts">
  import { getPsiThresholdKeyValue, hasConsoleConfig, hasOpsGenieConfig, hasSlackConfig } from "../types";
  import type { PsiAlertConfig, PsiDriftConfig } from "./psi";
  import Pill from "$lib/components/utils/Pill.svelte";
  import UpdateModal from "../update/UpdateModal.svelte";
  import type { UiProfile } from "../util";
  import { onMount } from "svelte";
  import type { RegistryType } from "$lib/utils";

  // props
  let { 
    config,
    alertConfig,
    profile,
    uid, 
    registry,
  } = $props<{
    config: PsiDriftConfig;
    alertConfig: PsiAlertConfig;
    profile: UiProfile;
    uid: string;
    registry: RegistryType;
  }>();

  let thresholdTypeValue = $state<{"type": string, "value":  number}>(
      getPsiThresholdKeyValue(alertConfig.threshold)
    );

  onMount(() => {
      // Ensure the thresholdTypeValue is initialized correctly
      thresholdTypeValue = getPsiThresholdKeyValue(alertConfig.threshold);

    });

  </script>

<div class="grid grid-cols-1 gap-2 w-full h-auto">
  <div class="flex flex-row gap-2">
    <div class="items-center mr-2 font-bold text-primary-800">Config:</div>
    <Pill key="Schedule" value={alertConfig.schedule} textSize="text-sm"/>

    {#if alertConfig.threshold}
      <Pill key="Psi Threshold" value={thresholdTypeValue.value.toString()} textSize="text-sm"/>
    {/if}

  </div>

  <div class="flex flex-row gap-2">

    <div class="items-center mr-2 font-bold text-primary-800">Dispatch:</div>
    
    {#if hasSlackConfig(alertConfig.dispatch_config)}
      <Pill key="Slack Channel" value={alertConfig.dispatch_config.Slack.channel} textSize="text-sm"/>
    {/if}

    {#if hasOpsGenieConfig(alertConfig.dispatch_config)}
      <Pill key="OpsGenie Team" value={alertConfig.dispatch_config.OpsGenie.team} textSize="text-sm"/>
      <Pill key="OpsGenie Priority" value={alertConfig.dispatch_config.OpsGenie.priority} textSize="text-sm"/>
    {/if}

    {#if hasConsoleConfig(alertConfig.dispatch_config)}
      <Pill key="Console" value= {alertConfig.dispatch_config.Console.enabled} textSize="text-sm"/>
    {/if}
  </div>
  <div class="flex flex-row justify-start gap-2">
    <UpdateModal 
      registry={registry}
      config={config} 
      driftType={config.drift_type}
      profile={profile}
      uid={uid}
      />
  </div>
</div>