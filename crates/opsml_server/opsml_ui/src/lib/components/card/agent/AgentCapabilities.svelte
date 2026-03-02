<script lang="ts">
  import type { AgentCapabilities } from "./types";
  import { Zap, Check, X, Link } from 'lucide-svelte';

  let { capabilities } = $props<{ capabilities: AgentCapabilities }>();
</script>

<div class="rounded-base border-2 border-black shadow bg-surface-50 p-4">
  <div class="flex items-center gap-2 mb-4 pb-3 border-b-2 border-black">
    <div class="p-1.5 bg-primary-500 border-2 border-black rounded-base">
      <Zap class="w-4 h-4 text-white" />
    </div>
    <h3 class="text-sm font-black text-primary-950 uppercase tracking-wide">Capabilities</h3>
  </div>

  <div class="space-y-3">
    <!-- Core Capabilities -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
      <div class="flex items-center gap-2 px-3 py-2 rounded-base border-2 border-black shadow-small {capabilities.streaming ? 'bg-secondary-300' : 'bg-surface-200'}">
        {#if capabilities.streaming}
          <Check class="w-4 h-4 text-black flex-shrink-0" />
        {:else}
          <X class="w-4 h-4 text-black/40 flex-shrink-0" />
        {/if}
        <span class="text-xs font-black {capabilities.streaming ? 'text-black' : 'text-black/50'} uppercase tracking-wide">
          Streaming
        </span>
      </div>

      <div class="flex items-center gap-2 px-3 py-2 rounded-base border-2 border-black shadow-small {capabilities.pushNotifications ? 'bg-secondary-300' : 'bg-surface-200'}">
        {#if capabilities.pushNotifications}
          <Check class="w-4 h-4 text-black flex-shrink-0" />
        {:else}
          <X class="w-4 h-4 text-black/40 flex-shrink-0" />
        {/if}
        <span class="text-xs font-black {capabilities.pushNotifications ? 'text-black' : 'text-black/50'} uppercase tracking-wide">
          Push
        </span>
      </div>

      <div class="flex items-center gap-2 px-3 py-2 rounded-base border-2 border-black shadow-small {capabilities.extendedAgentCard ? 'bg-secondary-300' : 'bg-surface-200'}">
        {#if capabilities.extendedAgentCard}
          <Check class="w-4 h-4 text-black flex-shrink-0" />
        {:else}
          <X class="w-4 h-4 text-black/40 flex-shrink-0" />
        {/if}
        <span class="text-xs font-black {capabilities.extendedAgentCard ? 'text-black' : 'text-black/50'} uppercase tracking-wide">
          Ext Card
        </span>
      </div>
    </div>

    <!-- Extensions -->
    {#if capabilities.extensions.length > 0}
      <div class="space-y-2 pt-1">
        <div class="flex items-center gap-2 py-1 border-b border-black/20">
          <Link class="w-3.5 h-3.5 text-primary-800" />
          <span class="text-xs font-black text-primary-950 uppercase tracking-wide">Extensions</span>
          <span class="badge bg-primary-100 text-primary-800 border border-black text-xs font-bold">{capabilities.extensions.length}</span>
        </div>

        <div class="space-y-2">
          {#each capabilities.extensions as extension}
            <div class="p-3 rounded-base border-2 border-black bg-surface-50 shadow-small">
              <div class="flex items-start justify-between gap-2">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1">
                    <a
                      href={extension.uri}
                      target="_blank"
                      rel="noopener noreferrer"
                      class="text-xs font-bold text-primary-700 hover:text-primary-950 hover:underline truncate font-mono"
                    >
                      {extension.uri}
                    </a>
                    {#if extension.required}
                      <span class="badge text-error-900 border border-black bg-error-100 text-xs flex-shrink-0 shadow-small font-black uppercase">
                        Required
                      </span>
                    {/if}
                  </div>
                  {#if extension.description}
                    <p class="text-xs text-black/60 mt-1">{extension.description}</p>
                  {/if}
                  {#if extension.params}
                    <details class="mt-2">
                      <summary class="text-xs font-bold text-primary-700 cursor-pointer hover:text-primary-950">View Parameters</summary>
                      <pre class="mt-2 p-2 bg-surface-100 rounded-base border border-black text-xs overflow-x-auto font-mono">{JSON.stringify(extension.params, null, 2)}</pre>
                    </details>
                  {/if}
                </div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </div>
</div>
