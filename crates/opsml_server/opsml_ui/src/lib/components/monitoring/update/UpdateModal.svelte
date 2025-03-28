
<script lang="ts">
  import { Modal } from '@skeletonlabs/skeleton-svelte';
  import { z } from 'zod';
  import UpdateDispatch from './UpdateDispatch.svelte';
  import { validateSlack,validateCustomConfig, validateOpsGenie, getConfigParams, validatePsiConfig, validateSpcConfig,   } from './schema';
  import type {SpcConfigParams, PsiConfigParams, ConfigParams, CustomConfigParams} from './schema';
  import type {SlackConfigSchema, OpsGenieConfigSchema, CustomConfigSchema, PsiConfigSchema} from './schema';
  import type { DriftConfigType } from '../util';
  import { isSpcConfig, isCustomConfig, isPsiConfig } from '../util';
  import { DriftType } from '../types';
  import CustomFields from './CustomFields.svelte';
  import SpcFields from './SpcFields.svelte';
  import PsiFields from './PsiFields.svelte';


  function stringToBoolean(str: string): boolean {
      return str
          .toLowerCase() === 'true';
  }


  let { 
      config = $bindable(), 
      driftType= $bindable() 
    } = $props<{
      config: DriftConfigType,
      driftType: DriftType
    }>();

  // props
  let openState = $state(false);

  let slackErrors = $state<Partial<Record<keyof SlackConfigSchema, string>>>({});
  let opsGenieErrors = $state<Partial<Record<keyof OpsGenieConfigSchema, string>>>({});
  let customErrors = $state<Partial<Record<keyof CustomConfigSchema, string>>>({});
  let psiErrors = $state<Partial<Record<keyof PsiConfigSchema, string>>>({});
  let spcErrors = $state<Partial<Record<keyof SpcConfigParams, string>>>({});
  let configParams = $state(getConfigParams(config));
  

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
          const validated = validatePsiConfig(
            psiParams.schedule,
            psiParams.psi_threshold,
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

  function updateConfig(event: Event) {
    event.preventDefault();

    if (!validateForm()) {
      return;
    }

    console.log('Valid config:');
    // TODO: Handle form submission
    modalClose();
  }
  
  
  </script>
  
  <Modal
  open={openState}
  onOpenChange={(e) => (openState = e.open)}
  triggerBase="btn bg-primary-500 text-black shadow shadow-hover border-black border-2"
  contentBase="card p-2 bg-surface-50 border-2 border-black shadow max-w-screen-xl w-[700px] overflow-visible"
  backdropClasses="backdrop-blur-sm"
  >
  {#snippet trigger()}Update Config{/snippet}
  {#snippet content()}

  <form class="mx-auto rounded-2xl bg-surface-50 p-4 md:px-5" onsubmit={updateConfig}>
    <div class="grid grid-cols-2 gap-8 min-h-[300px]">
      <!-- Left Column -->
      <div class="flex flex-col">
        <header class="text-xl font-bold text-primary-800 mb-2">Update Config</header> 
        <p class="mb-4 text-left text-surface-950">Update the following config elements</p>
  
        {#if driftType === DriftType.Spc}
          <SpcFields bind:params={configParams as SpcConfigParams} bind:errors={spcErrors} />
        {:else if driftType === DriftType.Psi}
          <PsiFields bind:params={configParams as PsiConfigParams} bind:errors={psiErrors} />
        {:else if driftType === DriftType.Custom}
          <CustomFields bind:params={configParams as CustomConfigParams} bind:errors={customErrors} />
        {/if}
  
      <!-- Right Column -->
      <div class="border-l-2 border-primary-500 pl-2 h-full overflow-visible">
        <div class="h-full overflow-visible">
          <UpdateDispatch bind:dispatchConfig={configParams.dispatch_config} />
        </div>
      </div>
    </div>
  
    <footer class="flex justify-end gap-4 p-2 mt-6">
      <button type="button" class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={modalClose}>Cancel</button>
      <button type="submit" class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2">Submit</button>
    </footer>
  </form>
   
    
   
  {/snippet}
  </Modal>
  
  
  