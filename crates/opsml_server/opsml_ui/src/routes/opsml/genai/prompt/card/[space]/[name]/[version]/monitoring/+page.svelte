<script lang="ts">
  import MonitoringDashboard from '$lib/components/card/monitoring/MonitoringDashboard.svelte';
  import type { PageProps } from './$types';

  let { data }: PageProps = $props();
</script>

<MonitoringDashboard
  profiles={data.profiles}
  driftTypes={data.keys}
  initialName={data.currentName}
  initialNames={data.currentNames}
  initialDriftType={data.currentDriftType}
  initialProfile={data.currentProfile}
  initialMetrics={data.latestMetrics}
  initialMetricData={data.currentMetricData}
  initialMaxDataPoints={data.maxDataPoints}
  initialConfig={data.currentConfig}
  initialAlerts={data.currentAlerts}
  uid={data.metadata.uid}
  registryType={data.registryType}
  currentLLMRecords={data.currentLLMRecords}
/>
 