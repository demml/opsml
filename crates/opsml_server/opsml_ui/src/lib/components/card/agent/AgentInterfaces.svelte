<script lang="ts">
  import type { AgentInterface } from "./types";
  import { Globe, Layers, Package, Users } from 'lucide-svelte';

  let { interfaces } = $props<{ interfaces: AgentInterface[] }>();
</script>

<div class="rounded-base border-2 border-black shadow bg-surface-50 p-4">
  <div class="flex items-center gap-2 mb-4 pb-3 border-b-2 border-black">
    <div class="p-1.5 bg-tertiary-100 border-2 border-black rounded-base">
      <Globe class="w-4 h-4 text-tertiary-950" />
    </div>
    <h3 class="text-sm font-black text-primary-950 uppercase tracking-wide">Interfaces</h3>
    <span class="badge bg-primary-100 text-primary-800 border border-black text-xs font-bold shadow-small px-2">{interfaces.length}</span>
  </div>

  {#if interfaces.length === 0}
    <div class="text-center py-8 text-black/40">
      <Globe class="w-10 h-10 mx-auto mb-2 opacity-40" />
      <p class="text-sm font-bold">No interfaces configured</p>
    </div>
  {:else}
    <div class="space-y-3">
      {#each interfaces as iface}
        <div class="p-3 rounded-base border-2 border-black bg-surface-50 shadow-small">
          <div class="space-y-2">

            <!-- Endpoint -->
            <div class="flex items-start gap-2">
              <Globe class="w-3.5 h-3.5 text-primary-700 mt-0.5 flex-shrink-0" />
              <div class="flex-1 min-w-0">
                <span class="text-xs font-black text-primary-700 block mb-1 uppercase tracking-wide">Endpoint</span>
                <a
                  href={iface.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-xs font-mono text-primary-700 hover:text-primary-950 hover:underline break-all"
                >
                  {iface.url}
                </a>
              </div>
            </div>

            <!-- Protocol Details -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div class="flex items-start gap-2 p-2 bg-surface-100 rounded-base border-2 border-black">
                <Layers class="w-3.5 h-3.5 text-secondary-700 mt-0.5 flex-shrink-0" />
                <div>
                  <span class="text-xs font-black text-primary-700 block uppercase tracking-wide">Binding</span>
                  <span class="text-xs text-primary-950 font-bold">{iface.protocolBinding}</span>
                </div>
              </div>
              <div class="flex items-start gap-2 p-2 bg-surface-100 rounded-base border-2 border-black">
                <Package class="w-3.5 h-3.5 text-secondary-700 mt-0.5 flex-shrink-0" />
                <div>
                  <span class="text-xs font-black text-primary-700 block uppercase tracking-wide">Version</span>
                  <span class="text-xs text-primary-950 font-bold">{iface.protocolVersion}</span>
                </div>
              </div>
            </div>

            <!-- Tenant -->
            {#if iface.tenant}
              <div class="flex items-start gap-2 p-2 bg-primary-100 rounded-base border-2 border-black">
                <Users class="w-3.5 h-3.5 text-primary-800 mt-0.5 flex-shrink-0" />
                <div>
                  <span class="text-xs font-black text-primary-700 block uppercase tracking-wide">Tenant</span>
                  <span class="text-xs text-primary-950 font-bold">{iface.tenant}</span>
                </div>
              </div>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
