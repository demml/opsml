<script lang="ts">
  import { AlertCircle, Activity, ArrowLeft, BookOpen } from 'lucide-svelte';
  import { getRegistryPath, type RegistryType } from '$lib/utils';

  interface Props {
    message: string;
    space: string;
    name: string;
    version: string;
    registryType: RegistryType;
  }

  let { message, space, name, version, registryType }: Props = $props();

  /**
   * Determine if this is a "not found" vs "error" scenario
   */
  let isNotFound = $derived(
    message.toLowerCase().includes('no drift profile') ||
    message.toLowerCase().includes('not found')
  );

  /**
   * Return path to card
   */
  let returnPath = $derived(
    `/opsml/${getRegistryPath(registryType)}/card/${space}/${name}/${version}/card`
  );
</script>

<div class="mx-auto w-full max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
  <!-- Neo-Brutalist Error Container -->
  <div class="bg-white shadow border-black border-2 rounded-lg">
    <div class="p-8 sm:p-12">
      <!-- Error Icon and Status -->
      <div class="flex flex-col items-center text-center">
        <div class="mb-6 relative">
          {#if isNotFound}
            <!-- Activity icon with diagonal line for "not found" -->
            <div class="relative">
              <Activity
                size={80}
                strokeWidth={2.5}
                class="text-gray-300"
              />
              <div class="absolute inset-0 flex items-center justify-center">
                <div class="w-24 h-1 bg-error-600 rotate-45 rounded-full"></div>
              </div>
            </div>
          {:else}
            <!-- Alert circle for errors -->
            <AlertCircle 
              size={80} 
              strokeWidth={2.5}
              class="text-error-600"
            />
          {/if}
        </div>

        <!-- Error Title -->
        <h1 class="text-3xl sm:text-4xl font-bold text-black mb-4 tracking-tight">
          {isNotFound ? 'Monitoring Unavailable' : 'Error Loading Monitoring'}
        </h1>

        <!-- Error Message -->
        <p class="text-lg text-gray-700 mb-8 max-w-2xl">
          {message}
        </p>

        <!-- Helpful Information Box (only for "not found") -->
        {#if isNotFound}
          <div class="w-full max-w-xl mb-8 bg-secondary-50 border-3 border-secondary-300 p-6 text-left">
            <h2 class="text-lg font-bold text-black mb-3 flex items-center gap-2">
              <Activity size={20} class="text-secondary-500" />
              What is Drift Monitoring?
            </h2>
            <p class="text-sm text-gray-700 mb-3">
              Drift monitoring tracks changes in your model's input data and predictions over time, 
              helping you detect when model performance may degrade.
            </p>
            <p class="text-sm text-gray-600">
              To enable monitoring, configure a drift profile when registering your model with OpsML.
            </p>
          </div>
        {/if}

        <!-- Action Buttons -->
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href={returnPath}
            class="
              inline-flex items-center justify-center gap-2 px-6 py-3
              bg-primary-500 text-white font-bold text-base
              border-3 border-black
              shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]
              hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]
              hover:translate-x-[2px] hover:translate-y-[2px]
              active:shadow-none active:translate-x-[4px] active:translate-y-[4px]
              transition-all duration-150
            "
          >
            <ArrowLeft size={20} />
            <span>Return to Card</span>
          </a>

          {#if isNotFound}
            <a
              href="https://docs.opsml.io"
              target="_blank"
              rel="noopener noreferrer"
              class="
                inline-flex items-center justify-center gap-2 px-6 py-3
                bg-white text-black font-bold text-base
                border-3 border-black
                shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]
                hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]
                hover:translate-x-[2px] hover:translate-y-[2px]
                active:shadow-none active:translate-x-[4px] active:translate-y-[4px]
                transition-all duration-150
              "
            >
              <BookOpen size={20} />
              <span>View Documentation</span>
            </a>
          {/if}
        </div>
      </div>
    </div>

    <!-- Footer with Model Info -->
    <div class="border-t-3 border-black bg-gray-50 px-8 py-4">
      <p class="text-center text-sm text-gray-600 font-mono">
        {space}/{name}:{version}
      </p>
    </div>
  </div>
</div>