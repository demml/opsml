<script lang="ts">
  import { hasConsoleConfig, hasOpsGenieConfig, hasSlackConfig } from "../utils";
  import type {  CustomDriftProfile, CustomMetricAlertConfig, CustomMetricDriftConfig } from "./types";
  import Pill from "$lib/components/utils/Pill.svelte";
  import UpdateModal from "$lib/components/scouter/update/UpdateModal.svelte";
  import type { UiProfile } from "../utils";
  import type { RegistryType } from "$lib/utils";

  // props
  let {
    config,
    alertConfig,
    profile,
    profileUri,
    uid,
    registry,
  } = $props<{
    config: CustomMetricDriftConfig;
    alertConfig: CustomMetricAlertConfig;
    profile: CustomDriftProfile;
    profileUri: String;
    uid: string;
    registry: RegistryType;
  }>();


  </script>

<div class="grid grid-cols-1 gap-2 w-full h-auto">
  <div class="flex flex-row gap-2">
    <div class="items-center mr-2 font-bold text-primary-800">Config:</div>
    <Pill key="Schedule" value={alertConfig.schedule} textSize="text-sm"/>
    {#if config.sample}
      <Pill key="Sample size" value={config.sample_size} textSize="text-sm"/>
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
      config={config}
      driftType={config.drift_type}
      profile={profile}
      profileUri={profileUri}
      uid={uid}
      registry={registry}
      />

  </div>
</div>