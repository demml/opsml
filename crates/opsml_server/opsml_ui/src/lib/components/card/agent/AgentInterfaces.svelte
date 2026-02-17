<script lang="ts">
  import type { AgentInterface } from "./types";
  import { Globe, Layers, Package, Users } from 'lucide-svelte';

  let { interfaces } = $props<{ interfaces: AgentInterface[] }>();
</script>

<div class="rounded-lg border-2 border-black shadow-small bg-surface-50 p-4">
  <div class="flex items-center gap-2 mb-4 pb-3 border-b-2 border-black">
    <div class="p-2 bg-tertiary-100 rounded-lg border-2 border-black">
      <Globe class="w-5 h-5 text-tertiary-950" />
    </div>
    <h3 class="text-lg font-bold text-primary-950">Supported Interfaces ({interfaces.length})</h3>
  </div>

  {#if interfaces.length === 0}
    <div class="text-center py-8 text-gray-500">
      <Globe class="w-12 h-12 mx-auto mb-2 opacity-50" />
      <p class="text-sm">No interfaces configured</p>
    </div>
  {:else}
    <div class="space-y-3">
      {#each interfaces as iface}
        <div class="p-4 rounded-lg border-2 border-black bg-white hover:bg-surface-50 transition-colors">
          <div class="space-y-3">
            <!-- URL -->
            <div class="flex items-start gap-2">
              <Globe class="w-4 h-4 text-primary-800 mt-0.5 flex-shrink-0" />
              <div class="flex-1 min-w-0">
                <span class="text-xs font-bold text-gray-600 block mb-1">Endpoint</span>
                <a 
                  href={iface.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  class="text-sm font-mono text-primary-600 hover:text-primary-800 hover:underline break-all"
                >
                  {iface.url}
                </a>
              </div>
            </div>

            <!-- Protocol Details -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div class="flex items-start gap-2 p-2 bg-surface-100 rounded border border-gray-300">
                <Layers class="w-4 h-4 text-secondary-800 mt-0.5 flex-shrink-0" />
                <div>
                  <span class="text-xs font-bold text-gray-600 block">Protocol Binding</span>
                  <span class="text-sm text-gray-900">{iface.protocolBinding}</span>
                </div>
              </div>

              <div class="flex items-start gap-2 p-2 bg-surface-100 rounded border border-gray-300">
                <Package class="w-4 h-4 text-secondary-800 mt-0.5 flex-shrink-0" />
                <div>
                  <span class="text-xs font-bold text-gray-600 block">Protocol Version</span>
                  <span class="text-sm text-gray-900">{iface.protocolVersion}</span>
                </div>
              </div>
            </div>

            <!-- Tenant -->
            {#if iface.tenant}
              <div class="flex items-start gap-2 p-2 bg-primary-50 rounded border border-primary-300">
                <Users class="w-4 h-4 text-primary-800 mt-0.5 flex-shrink-0" />
                <div>
                  <span class="text-xs font-bold text-gray-600 block">Tenant</span>
                  <span class="text-sm text-gray-900">{iface.tenant}</span>
                </div>
              </div>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
