<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { debounce } from '$lib/utils';
  import type { BaseProfileDashboardState } from './types';

  let {
    state
  }: {
    state: BaseProfileDashboardState
  } = $props();

  const debouncedCheckScreenSize = debounce(() => state.checkScreenSize(), 400);

  onMount(() => {
    window.addEventListener('resize', debouncedCheckScreenSize);
  });

  onDestroy(() => {
    window.removeEventListener('resize', debouncedCheckScreenSize);
  });
</script>