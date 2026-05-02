<script lang="ts">
  import AgentGenAiDashboard from '$lib/components/card/agent/observability/AgentGenAiDashboard.svelte';
  import ScouterRequiredView from '$lib/components/scouter/ScouterRequiredView.svelte';
  import { Sparkles } from 'lucide-svelte';
  import type { PageProps } from './$types';
  import { uiSettingsStore } from '$lib/components/settings/settings.svelte';
  import { devMockStore } from '$lib/components/settings/mockMode.svelte';

  let { data }: PageProps = $props();
  let scouterEnabled = $derived(uiSettingsStore.scouterEnabled);
  let mockEnabled = $derived(devMockStore.enabled);
</script>

{#if scouterEnabled || mockEnabled}
  <AgentGenAiDashboard bundle={data.bundle} />
{:else}
  <ScouterRequiredView
    featureName="GenAI Dashboard"
    featureDescription="Track GenAI token usage, cost, latency, and tool calls with real-time observability powered by Scouter."
    icon={Sparkles}
  />
{/if}
