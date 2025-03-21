<script lang="ts">
    import { DriftType } from "./types";
    import { getProfileConfig, getProfileFeatures, type DriftProfile, type DriftProfileResponse } from "./util";
    import { Clock } from 'lucide-svelte';
    import { TimeInterval } from '$lib/components/monitoring/types';
    import Dropdown from '$lib/components/utils/Dropdown.svelte';
    import { KeySquare } from 'lucide-svelte';
  import type { CustomMetricAlertConfig, CustomMetricDriftConfig } from "./custom";
  
    // props
    let { 
      config,
    } = $props<{
      config: CustomMetricDriftConfig;
    }>();
  

    let alertConfig: CustomMetricAlertConfig = config.alert_config;
  </script>

<div class="grid grid-cols-1 gap-4 w-full h-auto">
  <div class="flex justify-between">
    <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit">
      <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Space</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
        {config.repository}
      </div>
    </div>
    <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit">
      <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Space</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
        {config.repository}
      </div>
    </div>
    <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit">
      <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Space</div> 
      <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
        {config.repository}
      </div>
    </div>
  </div>
</div>