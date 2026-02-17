<script lang="ts">
  import type { AgentCapabilities } from "./types";
  import { Zap, Check, X, Link } from 'lucide-svelte';

  let { capabilities } = $props<{ capabilities: AgentCapabilities }>();
</script>

<div class="rounded-lg border-2 border-black shadow-small bg-surface-50 p-4">
  <div class="flex items-center gap-2 mb-4 pb-3 border-b-2 border-black">
    <div class="p-2 bg-primary-100 rounded-lg border-2 border-black">
      <Zap class="w-5 h-5 text-primary-800" />
    </div>
    <h3 class="text-lg font-bold text-primary-950">Capabilities</h3>
  </div>

  <div class="space-y-3">
    <!-- Core Capabilities -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
      <div class="flex items-center gap-1.5 px-2 py-1.5 rounded-lg border-2 border-black {capabilities.streaming ? 'bg-success-300' : 'bg-surface-200'}">
        {#if capabilities.streaming}
          <Check class="w-3.5 h-3.5 text-success-900" />
        {:else}
          <X class="w-3.5 h-3.5 text-gray-500" />
        {/if}
        <span class="text-xs font-bold {capabilities.streaming ? 'text-success-900' : 'text-gray-600'}">
          Streaming
        </span>
      </div>

      <div class="flex items-center gap-1.5 px-2 py-1.5 rounded-lg border-2 border-black {capabilities.pushNotifications ? 'bg-success-300' : 'bg-surface-200'}">
        {#if capabilities.pushNotifications}
          <Check class="w-3.5 h-3.5 text-success-900" />
        {:else}
          <X class="w-3.5 h-3.5 text-gray-500" />
        {/if}
        <span class="text-xs font-bold {capabilities.pushNotifications ? 'text-success-900' : 'text-gray-600'}">
          Push Notifications
        </span>
      </div>

      <div class="flex items-center gap-1.5 px-2 py-1.5 rounded-lg border-2 border-black {capabilities.extendedAgentCard ? 'bg-success-300' : 'bg-surface-200'}">
        {#if capabilities.extendedAgentCard}
          <Check class="w-3.5 h-3.5 text-success-900" />
        {:else}
          <X class="w-3.5 h-3.5 text-gray-500" />
        {/if}
        <span class="text-xs font-bold {capabilities.extendedAgentCard ? 'text-success-900' : 'text-gray-600'}">
          Extended Card
        </span>
      </div>
    </div>

    <!-- Extensions -->
    {#if capabilities.extensions.length > 0}
      <div class="space-y-2 pt-2">
        <div class="flex items-center gap-2">
          <Link class="w-4 h-4 text-primary-800" />
          <span class="text-sm font-bold text-primary-950">Extensions ({capabilities.extensions.length})</span>
        </div>

        <div class="space-y-2">
          {#each capabilities.extensions as extension}
            <div class="p-3 rounded-lg border-2 border-black bg-white">
              <div class="flex items-start justify-between gap-2">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1">
                    <a 
                      href={extension.uri} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      class="text-sm font-bold text-primary-600 hover:text-primary-800 hover:underline truncate"
                    >
                      {extension.uri}
                    </a>
                    {#if extension.required}
                      <span class="badge text-error-900 border-error-800 border-1 bg-error-100 text-xs flex-shrink-0">
                        Required
                      </span>
                    {/if}
                  </div>
                  
                  {#if extension.description}
                    <p class="text-xs text-gray-600 mt-1">{extension.description}</p>
                  {/if}

                  {#if extension.params}
                    <details class="mt-2">
                      <summary class="text-xs font-bold text-gray-700 cursor-pointer hover:text-primary-800">
                        View Parameters
                      </summary>
                      <pre class="mt-2 p-2 bg-surface-100 rounded border border-gray-300 text-xs overflow-x-auto">{JSON.stringify(extension.params, null, 2)}</pre>
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
