<script lang="ts">
  import MonitoringDashboard from '$lib/components/card/monitoring/MonitoringDashboard.svelte';
  import MonitoringErrorView from '$lib/components/card/monitoring/MonitoringErrorView.svelte';
  import type { PageProps } from './$types';
  import { uiSettingsStore } from '$lib/components/settings/settings.svelte';
  import ScouterRequiredView from '$lib/components/scouter/ScouterRequiredView.svelte';
  import { Activity } from 'lucide-svelte';

  let { data }: PageProps = $props();
  let scouterEnabled = $derived(uiSettingsStore.scouterEnabled);

</script>

{#if scouterEnabled}
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
      currentLLMRecords={data.data.currentLLMRecords}
    />
  {/if}
{:else}
  <ScouterRequiredView
    featureName="Monitoring Dashboard"
    featureDescription="Gain real-time insights into your model's performance, track key metrics, and receive alerts on anomalies with our comprehensive monitoring dashboard powered by Scouter."
    icon={Activity}
  />
{/if}