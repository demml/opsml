<script lang="ts">
  import MonitoringDashboard from '$lib/components/card/monitoring/MonitoringDashboard.svelte';
  import MonitoringErrorView from '$lib/components/card/monitoring/MonitoringErrorView.svelte';
  import type { PageProps } from './$types';

  let { data }: PageProps = $props();
</script>

{#if data.status === 'error'}
  <MonitoringErrorView
    message={data.errorMessage}
    space={data.metadata.space}
    name={data.metadata.name}
    version={data.metadata.version}
    registryType={data.registryType}
  />
{:else}
  <MonitoringDashboard
    profiles={data.data.profiles}
    driftTypes={data.data.keys}
    initialName={data.data.currentName}
    initialNames={data.data.currentNames}
    initialDriftType={data.data.currentDriftType}
    initialProfile={data.data.currentProfile}
    initialMetrics={data.data.latestMetrics}
    initialMetricData={data.data.currentMetricData}
    initialMaxDataPoints={data.data.maxDataPoints}
    initialConfig={data.data.currentConfig}
    initialAlerts={data.data.currentAlerts}
    uid={data.metadata.uid}
    registryType={data.registryType}
  />
{/if}