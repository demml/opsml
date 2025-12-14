<script lang="ts">
  import { AlertCircle, Activity, ArrowLeft, RefreshCw } from 'lucide-svelte';
  import { browser } from '$app/environment';

  interface Props {
    message: string;
    type?: 'error' | 'not_found';
  }

  let { message, type = 'error' }: Props = $props();

  let isNotFound = $derived(
    type === 'not_found' ||
    message.toLowerCase().includes('no trace found') ||
    message.toLowerCase().includes('not found')
  );

  let errorTimestamp = $state<string>('');

  $effect(() => {
    if (browser) {
      errorTimestamp = new Date().toLocaleString();
    }
  });

</script>

<div class="mx-auto w-full max-w-4xl px-4 py-6 sm:px-6 lg:px-8">
  <div class="flex items-center justify-between mb-4">
    <h1 class="text-2xl font-bold text-primary-800">
      {isNotFound ? 'No Traces Found' : 'Error Loading Traces'}
    </h1>
  </div>

  <div class="pb-1 pr-1">
    <div class="bg-white border-2 border-black rounded-lg shadow">
      <div class="p-8 sm:p-12">
        <div class="flex flex-col items-center text-center">
          <div class="mb-6 relative">
            {#if isNotFound}
              <div class="relative">
                <Activity size={80} strokeWidth={2.5} class="text-gray-300" />
                <div class="absolute inset-0 flex items-center justify-center">
                  <div class="w-24 h-1 bg-error-600 rotate-45 rounded-full"></div>
                </div>
              </div>
            {:else}
              <AlertCircle size={80} strokeWidth={2.5} class="text-error-600" />
            {/if}
          </div>

          <h2 class="text-3xl sm:text-4xl font-bold text-black mb-4 tracking-tight">
            {isNotFound ? 'No Traces Available' : 'Error Loading Traces'}
          </h2>

          <p class="text-lg text-gray-700 mb-8 max-w-2xl">
            {message}
          </p>

          {#if isNotFound}
            <div class="w-full max-w-xl mb-8 bg-primary-50 border-2 border-primary-500 p-6 text-left rounded-lg">
              <h3 class="text-lg font-bold text-black mb-3 flex items-center gap-2">
                <Activity size={20} class="text-primary-500" />
                What is Tracing?
              </h3>
              <p class="text-sm text-gray-700 mb-3">
                Distributed tracing helps you understand request flows across your services,
                identify performance bottlenecks, and debug issues in complex systems.
              </p>
              <p class="text-sm text-gray-600">
                Try adjusting the time range above or check if your application is generating traces.
              </p>
            </div>
          {/if}

          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/opsml/home"
              class="
                inline-flex items-center justify-center gap-2 px-6 py-3
                bg-primary-500 text-black font-bold text-base
                border-2 border-black rounded-lg shadow
                shadow-hover"
            >
              <ArrowLeft size={20} />
              <span>Return to Home</span>
            </a>
          </div>
        </div>
      </div>

      {#if browser && errorTimestamp}
        <div class="border-t-2 border-black bg-gray-50 px-8 py-4 rounded-b-lg">
          <p class="text-center text-sm text-gray-600 font-mono">
            Time: {errorTimestamp}
          </p>
        </div>
      {/if}
    </div>
  </div>
</div>