<script lang="ts">
  import { AlertCircle, Activity, ArrowLeft, RefreshCw } from 'lucide-svelte';
  import { invalidate } from '$app/navigation';
  import { browser } from '$app/environment';
  import TimeRangeFilter, { type TimeRange } from './TimeRangeFilter.svelte';
  import type { DateTime } from '$lib/types';
  import { setCookie } from './utils';

  interface Props {
    message: string;
    type?: 'error' | 'not_found';
    initialFilters?: {
      start_time: DateTime;
      end_time: DateTime;
      bucket_interval: string;
      selected_range: string;
    };
  }

  let { message, type = 'error', initialFilters }: Props = $props();

  let isNotFound = $derived(
    type === 'not_found' ||
    message.toLowerCase().includes('no traces') ||
    message.toLowerCase().includes('not found')
  );

  let errorTimestamp = $state<string>('');
  let isUpdating = $state(false);

  /**
   * Create TimeRange object from stored range value
   */
  function createTimeRangeFromValue(rangeValue: string): TimeRange {
    const labels: Record<string, string> = {
      '15min': 'Past 15 Minutes',
      '30min': 'Past 30 Minutes',
      '1hour': 'Past 1 Hour',
      '4hours': 'Past 4 Hours',
      '12hours': 'Past 12 Hours',
      '24hours': 'Past 24 Hours',
      '7days': 'Past 7 Days',
      '30days': 'Past 30 Days',
    };

    return {
      label: labels[rangeValue] || 'Past 15 Minutes',
      value: rangeValue,
      startTime: initialFilters?.start_time || (new Date(Date.now() - 15 * 60 * 1000).toISOString() as DateTime),
      endTime: initialFilters?.end_time || (new Date().toISOString() as DateTime),
      bucketInterval: initialFilters?.bucket_interval || '1 minutes',
    };
  }

  let selectedTimeRange = $state<TimeRange>(
    createTimeRangeFromValue(initialFilters?.selected_range || '15min')
  );

  $effect(() => {
    if (browser) {
      errorTimestamp = new Date().toLocaleString();
    }
  });

  /**
   * Handle refresh - reloads with current time range
   */
  async function handleRefresh() {
    isUpdating = true;
    try {
      await invalidate('trace:data');
    } catch (error) {
      console.error('Failed to refresh traces:', error);
    } finally {
      isUpdating = false;
    }
  }

  /**
   * Handle time range changes by storing only the range value
   */
  async function handleTimeRangeChange(range: TimeRange) {
    selectedTimeRange = range;
    isUpdating = true;

    try {
      // Only store the range value, not absolute timestamps
      setCookie('trace_range', range.value);

      // Trigger reload - timestamps will be calculated fresh
      await invalidate('trace:data');
    } catch (error) {
      console.error('Failed to update time range:', error);
    } finally {
      isUpdating = false;
    }
  }
</script>

<div class="mx-auto w-full max-w-4xl px-4 py-6 sm:px-6 lg:px-8">
  <div class="flex items-center justify-between mb-4">
    <h1 class="text-2xl font-bold text-primary-800">
      {isNotFound ? 'No Traces Found' : 'Error Loading Traces'}
      {#if isUpdating}
        <span class="text-sm font-normal text-gray-500 ml-2">Updating...</span>
      {/if}
    </h1>
    {#if isNotFound}
      <TimeRangeFilter
        selectedRange={selectedTimeRange}
        onRangeChange={handleTimeRangeChange}
      />
    {/if}
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
                What is Trace Monitoring?
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
            <button
              onclick={handleRefresh}
              disabled={isUpdating}
              class="
                inline-flex items-center justify-center gap-2 px-6 py-3
                bg-primary-500 text-white font-bold text-base
                border-2 border-black rounded-lg shadow
                hover:shadow-lg hover:translate-x-[-2px] hover:translate-y-[-2px]
                active:shadow-sm active:translate-x-0 active:translate-y-0
                transition-all duration-150
                disabled:opacity-50 disabled:cursor-not-allowed
              "
            >
              <RefreshCw size={20} class={isUpdating ? 'animate-spin' : ''} />
              <span>Retry</span>
            </button>

            <a
              href="/opsml/home"
              class="
                inline-flex items-center justify-center gap-2 px-6 py-3
                bg-white text-black font-bold text-base
                border-2 border-black rounded-lg shadow
                hover:shadow-lg hover:translate-x-[-2px] hover:translate-y-[-2px]
                active:shadow-sm active:translate-x-0 active:translate-y-0
                transition-all duration-150
              "
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
            Error occurred at {errorTimestamp}
          </p>
        </div>
      {/if}
    </div>
  </div>
</div>