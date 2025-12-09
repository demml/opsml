<script lang="ts">
  import { Calendar, Clock, ChevronDown } from 'lucide-svelte';
  import type { DateTime } from '$lib/types';

  export interface TimeRange {
    label: string;
    value: string;
    startTime: DateTime;
    endTime: DateTime;
    bucketInterval: string;
  }

  let {
    selectedRange = $bindable(),
    onRangeChange
  }: {
    selectedRange: TimeRange;
    onRangeChange: (range: TimeRange) => void;
  } = $props();

  let isOpen = $state(false);
  let showCustomPicker = $state(false);
  let customStartDate = $state('');
  let customStartTime = $state('');
  let customEndDate = $state('');
  let customEndTime = $state('');

  function getBucketInterval(value: string): string {
  switch (value) {
    case '15min':
      return '30 seconds';
    case '30min':
      return '1 minutes';
    case '1hour':
      return '1 minutes';
    case '4hours':
      return '2 minutes';
    case '12hours':
      return '5 minutes';
    case '24hours':
      return '10 minutes';
    case '7days':
      return '1 hours';
    case '30days':
      return '4 hours';
    default:
      return '1 minutes';
  }
}

  const PRESET_RANGES: Omit<TimeRange, 'startTime' | 'endTime' | 'bucketInterval'>[] = [
    { label: 'Live (15min)', value: '15min' },
    { label: 'Past 15 Minutes', value: '15min' },
    { label: 'Past 30 Minutes', value: '30min' },
    { label: 'Past 1 Hour', value: '1hour' },
    { label: 'Past 4 Hours', value: '4hours' },
    { label: 'Past 12 Hours', value: '12hours' },
    { label: 'Past 24 Hours', value: '24hours' },
    { label: 'Past 7 Days', value: '7days' },
    { label: 'Past 30 Days', value: '30days' },
];

  function calculateTimeRange(value: string): { startTime: DateTime; endTime: DateTime; bucketInterval: string } {
    const now = new Date();
    const endTime = now.toISOString() as DateTime;
    let startTime: DateTime;
    const bucketInterval = getBucketInterval(value);

    switch (value) {
      case '15min':
        startTime = new Date(now.getTime() - 15 * 60 * 1000).toISOString() as DateTime;
        break;
      case '30min':
        startTime = new Date(now.getTime() - 30 * 60 * 1000).toISOString() as DateTime;
        break;
      case '1hour':
        startTime = new Date(now.getTime() - 60 * 60 * 1000).toISOString() as DateTime;
        break;
      case '4hours':
        startTime = new Date(now.getTime() - 4 * 60 * 60 * 1000).toISOString() as DateTime;
        break;
      case '12hours':
        startTime = new Date(now.getTime() - 12 * 60 * 60 * 1000).toISOString() as DateTime;
        break;
      case '24hours':
        startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000).toISOString() as DateTime;
        break;
      case '7days':
        startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString() as DateTime;
        break;
      case '30days':
        startTime = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString() as DateTime;
        break;
      default:
        startTime = new Date(now.getTime() - 15 * 60 * 1000).toISOString() as DateTime;
    }

    return { startTime, endTime, bucketInterval };
  }

  function handlePresetSelect(preset: typeof PRESET_RANGES[0]) {
    const { startTime, endTime, bucketInterval } = calculateTimeRange(preset.value);
    const range: TimeRange = {
      label: preset.label,
      value: preset.value,
      startTime,
      endTime,
      bucketInterval,
    };
    selectedRange = range;
    onRangeChange(range);
    isOpen = false;
    showCustomPicker = false;
  }

  function handleCustomRange() {
  if (!customStartDate || !customEndDate) {
    alert('Please select both start and end dates');
    return;
  }

  const startDateTime = new Date(`${customStartDate}T${customStartTime || '00:00:00'}`);
  const endDateTime = new Date(`${customEndDate}T${customEndTime || '23:59:59'}`);

  if (isNaN(startDateTime.getTime()) || isNaN(endDateTime.getTime())) {
    alert('Invalid date or time selected');
    return;
  }

  const startTime = startDateTime.toISOString() as DateTime;
  const endTime = endDateTime.toISOString() as DateTime;

  if (startTime >= endTime) {
    alert('Start time must be before end time');
    return;
  }

  // Calculate optimal bucket for custom range
  const durationMs = endDateTime.getTime() - startDateTime.getTime();
  const bucketInterval = calculateCustomBucketInterval(durationMs);

  const range: TimeRange = {
    label: 'Custom Range',
    value: 'custom',
    startTime,
    endTime,
    bucketInterval,
  };
  selectedRange = range;
  onRangeChange(range);
  isOpen = false;
  showCustomPicker = false;
}

function calculateCustomBucketInterval(durationMs: number): string {
  const targetBuckets = 150;
  const bucketMs = durationMs / targetBuckets;

  // Round to sensible intervals
  if (bucketMs < 60_000) { // < 1 minute
    return '30 seconds';
  } else if (bucketMs < 5 * 60_000) { // < 5 minutes
    return '1 minutes';
  } else if (bucketMs < 15 * 60_000) { // < 15 minutes
    return '5 minutes';
  } else if (bucketMs < 60 * 60_000) { // < 1 hour
    return '10 minutes';
  } else if (bucketMs < 4 * 60 * 60_000) { // < 4 hours
    return '1 hours';
  } else if (bucketMs < 24 * 60 * 60_000) { // < 24 hours
    return '4 hours';
  } else {
    return '1 days';
  }
}


  function toggleDropdown() {
    isOpen = !isOpen;
    if (!isOpen) {
      showCustomPicker = false;
    }
  }

  function showCustom(event: MouseEvent) {
    event.stopPropagation();
    showCustomPicker = true;
  }

  function handleClickOutside(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest('.time-range-filter')) {
      isOpen = false;
      showCustomPicker = false;
    }
  }

  $effect(() => {
    if (isOpen) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  });
</script>

<div class="time-range-filter relative">
  <button
    onclick={toggleDropdown}
    class="flex items-center gap-2 px-4 py-2 bg-white border-2 border-black rounded-lg shadow-small hover:shadow-hover hover:bg-primary-50 transition-all text-sm font-bold text-primary-800"
    aria-label="Select time range"
  >
    <Clock class="w-4 h-4" />
    <span>{selectedRange.label}</span>
    <ChevronDown class="w-4 h-4 transition-transform {isOpen ? 'rotate-180' : ''}" />
  </button>

  {#if isOpen}
    <div class="absolute right-0 mt-2 bg-white border-2 border-black rounded-lg shadow-primary z-50 overflow-hidden">
      {#if !showCustomPicker}
        <div class="max-h-96 overflow-y-auto">
          {#each PRESET_RANGES as preset}
            <button
              onclick={() => handlePresetSelect(preset)}
              class="w-full px-4 py-2 text-left text-sm hover:bg-primary-100 transition-colors border-b border-gray-200 last:border-b-0 {selectedRange.value === preset.value ? 'bg-primary-50 font-bold text-primary-800' : 'text-gray-700'}"
            >
              {preset.label}
            </button>
          {/each}
        </div>

        <button
          onclick={showCustom}
          class="w-full px-4 py-3 text-left text-sm font-bold bg-surface-200 hover:bg-primary-100 transition-colors border-t-2 border-black flex items-center gap-2 text-primary-800"
        >
          <Calendar class="w-4 h-4" />
          Custom Range
        </button>
      {:else}
        <div class="p-4 space-y-1 w-80">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-bold text-primary-800">Custom Time Range</h3>
            <button
              onclick={() => showCustomPicker = false}
              class="text-xs text-gray-500 hover:text-primary-800"
            >
              Back
            </button>
          </div>

          <div class="space-y-1">
            <label for="custom-start-date" class="block text-xs font-bold text-gray-700">Start</label>
            <div class="grid grid-cols-2 gap-2">
              <input
                id="custom-start-date"
                type="date"
                bind:value={customStartDate}
                class="date-input w-full px-2 py-1 text-sm border-2 border-black rounded focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <input
                id="custom-start-time"
                type="time"
                bind:value={customStartTime}
                class="time-input w-full px-2 py-1 text-sm border-2 border-black rounded focus:outline-none focus:ring-2 focus:ring-primary-500"
                aria-label="Start time"
              />
            </div>
          </div>

          <div class="space-y-1 pb-1">
            <label for="custom-end-date" class="block text-xs font-bold text-gray-700">End</label>
            <div class="grid grid-cols-2 gap-2">
              <input
                id="custom-end-date"
                type="date"
                bind:value={customEndDate}
                class="date-input w-full px-2 py-1 text-sm border-2 border-black rounded focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <input
                id="custom-end-time"
                type="time"
                bind:value={customEndTime}
                class="time-input w-full px-2 py-1 text-sm border-2 border-black rounded focus:outline-none focus:ring-2 focus:ring-primary-500"
                aria-label="End time"
              />
            </div>
          </div>

          <div class="flex justify-center pt-2">
            <button
              class="btn text-sm flex self-center gap-2 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg"
              onclick={handleCustomRange}
              >
            Apply
            </button>
          </div>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  /* Style the native calendar picker button for date inputs */
  .date-input::-webkit-calendar-picker-indicator {
    cursor: pointer;
    filter: invert(0);
    opacity: 0.8;
    padding: 4px;
    border-radius: 4px;
    background-color: var(--color-primary-500);
    opacity: 1;
  }

  /* Style the native clock picker button for time inputs */
  .time-input::-webkit-calendar-picker-indicator {
    cursor: pointer;
    filter: invert(0);
    opacity: 0.8;
    padding: 4px;
    border-radius: 4px;
    background-color: var(--color-primary-500);
    opacity: 1;
  }

  /* Ensure text color is black for better visibility */
  .date-input,
  .time-input {
    color: black;
  }
</style>