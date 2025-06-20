
<script lang="ts">
  import { Modal } from '@skeletonlabs/skeleton-svelte';
  import { z } from 'zod';
  import { validateSlack,validateCustomConfig, validateOpsGenie, getConfigParams, validatePsiConfig, validateSpcConfig, validateConsole  } from './schema';
  import type {SpcConfigParams, PsiConfigParams, ConfigParams, CustomConfigParams, ConsoleConfigSchema} from './schema';
  import type {SlackConfigSchema, OpsGenieConfigSchema, CustomConfigSchema, PsiConfigSchema} from './schema';
  import type { DriftConfigType, DriftProfile, UiProfile } from '../util';
  import { isSpcConfig, isCustomConfig, isPsiConfig, updateDriftProfile, extractProfile } from '../util';
  import { DriftType, getPsiThresholdKeyValue } from '../types';
  import CustomFields from './CustomFields.svelte';
  import SpcFields from './SpcFields.svelte';
  import PsiFields from './PsiFields.svelte';
  import { AlertDispatchType } from '../types';
  import Dropdown from '$lib/components/utils/Dropdown.svelte';
  import Slack from './dispatch/Slack.svelte';
  import OpsGenie from './dispatch/OpsGenie.svelte';
  import Console from './dispatch/Console.svelte';
  import type { SlackDispatchConfig,  OpsGenieDispatchConfig, ConsoleDispatchConfig} from '../types';
  import { hasSlackConfig, hasOpsGenieConfig } from '../types';
  import { type UpdateProfileRequest } from '../types';


  function getDispatchType(): string {
    
    if (hasSlackConfig(configParams.dispatch_config)) {
      return AlertDispatchType.Slack;
    } else if (hasOpsGenieConfig(configParams.dispatch_config)) {
      return AlertDispatchType.OpsGenie;
    } else {
      return AlertDispatchType.Console;
    }
  }

  let { 
    
      config = $bindable(), 
      driftType= $bindable(),
      profile= $bindable(),
      uid,
    } = $props<{
      config: DriftConfigType;
      driftType: DriftType;
      profile: UiProfile;
      uid: string;
    }>();

  // props
  let openState = $state(false);

  // errors state
  let slackErrors = $state<Partial<Record<keyof SlackConfigSchema, string>>>({});
  let opsGenieErrors = $state<Partial<Record<keyof OpsGenieConfigSchema, string>>>({});
  let consoleErrors = $state<Partial<Record<keyof ConsoleConfigSchema, string>>>({});
  let customErrors = $state<Partial<Record<keyof CustomConfigSchema, string>>>({});
  let psiErrors = $state<Partial<Record<keyof PsiConfigSchema, string>>>({});
  let spcErrors = $state<Partial<Record<keyof SpcConfigParams, string>>>({});

  // config state
  let configParams = $state(getConfigParams(config));

  // dispatch state
  let dispatchType = $state<string>(getDispatchType());
  let dispatchOptions = $state(Object.values(AlertDispatchType))
  

  function modalClose() {
      openState = false;
  }

  function validateForm(): boolean {
    // Reset all errors at start
    spcErrors = {};
    psiErrors = {};
    customErrors = {};

    switch (driftType) {
      case DriftType.Spc: {
        if (!isSpcConfig(config)) return false;
        
        const spcParams = configParams as SpcConfigParams;
  
        const validated = validateSpcConfig(
          spcParams.schedule,
          spcParams.sample,
          spcParams.sample_size,
          spcParams.rule,
          spcParams.features_to_monitor
        );

        if (!validated.success) {
          spcErrors = validated.errors ?? {};
          return false;
        }
        return true;
      }

      case DriftType.Psi: {
        if (!isPsiConfig(config)) return false;
        
        const psiParams = configParams as PsiConfigParams;
        const threshold = psiParams.threshold;

        let keyValue = getPsiThresholdKeyValue(threshold);
     
        const validated = validatePsiConfig(
          psiParams.schedule,
          keyValue.value,
          keyValue.type,
          psiParams.features_to_monitor
        );

        if (!validated.success) {
          psiErrors = validated.errors ?? {};
          return false;
        }
   
        return true;
      }

      case DriftType.Custom: {
        if (!isCustomConfig(config)) return false;

        const customParams = configParams as CustomConfigParams;
        const validated = validateCustomConfig(
        customParams.schedule,
        customParams.sample,
        customParams.sample_size
      );

      if (!validated.success) {
        customErrors = validated.errors ?? {};
        return false;
      }
      return true;
    }

    default:
      console.error('Unknown drift type:', driftType);
      return false;
  }
}

function validateDispatchForm(): boolean {
    const dispatchParams = configParams.dispatch_config;

    switch (dispatchType) {
      case AlertDispatchType.Slack: {
        const slackParams = dispatchParams.Slack as SlackDispatchConfig;
        const validated = validateSlack(
          slackParams.channel
        );

        if (!validated.success) {
          slackErrors = validated.errors ?? {};
          return false;
        }
        return true;
      }

      case AlertDispatchType.OpsGenie: {
        const opsGenieParams = dispatchParams.OpsGenie as OpsGenieDispatchConfig;
        const validated = validateOpsGenie(
          opsGenieParams.team,
          opsGenieParams.priority
        );

        if (!validated.success) {
          opsGenieErrors = validated.errors ?? {};
          return false;
        }
        return true;
      }

      case AlertDispatchType.Console: {
        const consoleParams = dispatchParams.Console as ConsoleDispatchConfig;
        const validated = validateConsole(
          consoleParams.enabled
        );

        if (!validated.success) {
          consoleErrors = validated.errors ?? {};
          return false;
        }
        return true;
      }

      default:
        console.error('Unknown dispatch type:', dispatchType);
        return false;
    }
    
  }

  async function updateConfig(event: Event) {
    event.preventDefault();

    if (!validateForm() || !validateDispatchForm()) {
      return;
    }

    // implement post request to update config
    const matchedProfile = extractProfile(profile.profile, driftType);


    matchedProfile.config = {
      ...matchedProfile.config,
      ...configParams
    };

    let request: UpdateProfileRequest = {
      uid: uid,
      profile_uri: profile.profile_uri,
      request: {
        space: matchedProfile.config.space,
        profile: JSON.stringify(matchedProfile),
        drift_type: driftType,
        
      }
    };

    await updateDriftProfile(request);

    modalClose();

  
  }

  function updateParamCallback(field: string, value: any) {

      // @ts-ignore
      configParams[field] = value;

      configParams = {
        ...configParams,
        [field]: value
      };

    }
  
 
    
  function updateDispatchParamCallback(field: string, value: string) {
      

    const newDispatchConfig = {
   
      [dispatchType]: {
        // @ts-ignore
        ...configParams.dispatch_config[dispatchType],
        [field]: value
      }
    };

      configParams = {
        ...configParams,
        dispatch_config: newDispatchConfig
      };
  }

  
  </script>
  
  <Modal
  open={openState}
  onOpenChange={(e) => (openState = e.open)}
  triggerBase="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 text-sm"
  contentBase="card p-2 bg-surface-50 border-2 border-black shadow max-w-screen-xl w-[700px] overflow-visible"
  backdropClasses="backdrop-blur-sm"
  >
  {#snippet trigger()}Update Config{/snippet}
  {#snippet content()}

  <form class="mx-auto rounded-2xl bg-surface-50 p-4 md:px-5" onsubmit={updateConfig}>
    <div class="grid grid-cols-2 gap-8 min-h-[300px]">
      <!-- Left Column -->
      <div class="flex flex-col">
        <header class="text-lg font-bold text-primary-800 mb-2">Update Config</header> 
        <p class="mb-4 text-left text-surface-950">Update the following config elements</p>
  
        {#if driftType === DriftType.Spc}
          <SpcFields 
            params={configParams as SpcConfigParams} 
            errors={spcErrors} 
            updateCallback={updateParamCallback}
            />
        {:else if driftType === DriftType.Psi}
          <PsiFields 
            params={configParams as PsiConfigParams} 
            errors={psiErrors} 
            updateCallback={updateParamCallback}
            />
        {:else if driftType === DriftType.Custom}
          <CustomFields 
            params={configParams as CustomConfigParams} 
            errors={customErrors} 
            updateCallback={updateParamCallback}
            />
        {/if}
      </div>

      <!-- Right Column -->
      <div class="border-l-2 border-primary-500 pl-2 h-full overflow-visible">

        <div class="flex flex-col overflow-auto min-h-full">
          <div class="flex flex-col pb-2 justify-between">
            <header class="pl-2 text-lg font-bold text-primary-800">Update Dispatch</header> 
            <Dropdown 
                  bind:selectedValue={dispatchType}
                  bind:values={dispatchOptions}
                  width='w-48'
                  py="py-2"
            />
          </div>

          <div class="h-full overflow-visible">
            {#if dispatchType === AlertDispatchType.Slack}
              <Slack 
                dispatchConfig={configParams.dispatch_config}
                errors={slackErrors}
                updateCallback={updateDispatchParamCallback}
              />
            {:else if dispatchType === AlertDispatchType.OpsGenie}
              <OpsGenie 
                dispatchConfig={configParams.dispatch_config}
                errors={opsGenieErrors} 
                updateCallback={updateDispatchParamCallback}
              />
            {:else if dispatchType === AlertDispatchType.Console}
              <Console
                dispatchConfig={configParams.dispatch_config}
                errors={consoleErrors}
                updateCallback={updateDispatchParamCallback}
              />
            {/if}
          </div>

        </div>
        
      </div>
  
    <footer class="flex justify-end gap-4 p-2 mt-6">
      <button type="button" class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={modalClose}>Cancel</button>
      <button type="submit" class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2">Submit</button>
    </footer>
  </form>
   
    
   
  {/snippet}
  </Modal>
  
  
  