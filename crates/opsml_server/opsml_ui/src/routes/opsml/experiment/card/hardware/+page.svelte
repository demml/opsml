<script lang="ts">
  import type { UiHardwareMetrics } from '$lib/components/card/experiment/types';
  import type { PageProps } from './$types';
  let { data }: PageProps = $props();

  let metrics: UiHardwareMetrics = data.hardwareMetrics;
</script>

<div class="flex-1 mx-auto w-9/12 pb-10 flex justify-center overflow-auto px-4">
</div>