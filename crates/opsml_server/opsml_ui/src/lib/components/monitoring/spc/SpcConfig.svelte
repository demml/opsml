<script lang="ts">

import type { SpcAlertConfig, SpcDriftConfig } from "./spc";
  
    // props
    let { 
      config,
    } = $props<{
      config: SpcDriftConfig;
    }>();
  

    let alertConfig: SpcAlertConfig= config.alert_config;
  </script>
  
  <div class="grid grid-cols-1 gap-4 w-full h-auto">
    <div class="flex justify-between">
      <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit">
        <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Schedule</div> 
        <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
          {config.schedule}
        </div>
      </div>
  
      {#if alertConfig.dispatch_config.type === 'Slack'}
        <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit">
          <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Slack Channel</div> 
          <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
            {alertConfig.dispatch_config.config.channel}
          </div>
        </div>
      {/if}
  
      {#if alertConfig.dispatch_config.type === 'OpsGenie'}
        <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit">
          <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">OpsGenie</div> 
          <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
            {alertConfig.dispatch_config.config.team}
          </div>
        </div>
      {/if}
  
      {#if alertConfig.dispatch_config.type === 'Console'}
        <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit">
          <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Console</div> 
          <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
            Console
          </div>
        </div>
      {/if}
    </div>
    <div class="flex justify-between">
      <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit">
        <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Monitored Features</div> 
        <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
          {alertConfig.features_to_monitor}
        </div>
      </div>
  
      <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit">
        <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Alert Rule</div> 
        <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
          {alertConfig.rule.rule}
        </div>
      </div>

      <div class="inline-flex items-center overflow-hidden rounded-lg border-2 border-primary-700 w-fit">
        <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic">Alert Zones</div> 
        <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950">
          {alertConfig.rule.zones_to_monitor}
        </div>
      </div>
    </div>
  </div>