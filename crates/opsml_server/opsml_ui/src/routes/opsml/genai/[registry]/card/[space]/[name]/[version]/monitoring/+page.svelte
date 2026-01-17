<script lang="ts">
  import MonitoringDashboard from '$lib/components/scouter/dashboard/MonitoringDashboard.svelte';
  import MonitoringErrorView from '$lib/components/scouter/dashboard/MonitoringErrorView.svelte';
  import type { PageProps } from './$types';
  import { uiSettingsStore } from '$lib/components/settings/settings.svelte';
  import ScouterRequiredView from '$lib/components/scouter/ScouterRequiredView.svelte';
  import { Activity } from 'lucide-svelte';
  import type { MonitoringPageData } from '$lib/components/scouter/dashboard/utils';

  let { data }: PageProps = $props();
  let scouterEnabled = $derived(uiSettingsStore.scouterEnabled);
  let pageData: MonitoringPageData = $state(data.monitoringData);

</script>

{#if scouterEnabled}`
  {#if pageData.status === 'error'}
    <MonitoringErrorView
      message={pageData.errorMsg}
      space={data.metadata.space}
      name={data.metadata.name}
      version={data.metadata.version}
      registryType={data.registryType}
    />
  {:else}
    <MonitoringDashboard {pageData} />
  {/if}
{:else}
  <ScouterRequiredView
    featureName="Monitoring Dashboard"
    featureDescription="Gain real-time insights into your model's performance, track key metrics, and receive alerts on anomalies with our comprehensive monitoring dashboard powered by Scouter."
    icon={Activity}
  />
{/if}