<script lang="ts">
  import type { Snippet } from 'svelte';
  import { uiSettingsStore } from '$lib/components/settings/settings.svelte';
  import ScouterRequiredView from '$lib/components/scouter/ScouterRequiredView.svelte';
  import { Sparkles } from 'lucide-svelte';
  import type { LayoutData } from './$types';
  import DashboardTimeBar from '$lib/components/utils/DashboardTimeBar.svelte';
  import { timeRangeState } from '$lib/components/utils/timeState.svelte';
  import { RegistryType } from '$lib/utils';
  import type { TimeRange } from '$lib/components/trace/types';
  import { setCookie } from '$lib/components/trace/utils';
  import type { PromptCard } from '$lib/components/card/card_interfaces/promptcard';

  let { data, children }: { data: LayoutData; children: Snippet } = $props();
  const scouterEnabled = $derived(uiSettingsStore.scouterEnabled);
  const mockMode = $derived(data.mockMode ?? false);
  const isPrompt = $derived(data.registryType === RegistryType.Prompt);

  const subtitle = $derived.by(() => {
    if (isPrompt) {
      const promptCard = data.metadata as PromptCard;
      const profile = promptCard.eval_profile;
      const tag = profile?.alias ?? profile?.config.uid ?? 'no-profile';
      return `${promptCard.space}/${promptCard.name} · profile ${tag}`;
    }
    return `${data.metadata.space}:${data.metadata.name} · v${data.metadata.version}`;
  });

  function handleRangeChange(newRange: TimeRange) {
    timeRangeState.updateTimeRange(newRange);
    setCookie('monitoring_range', newRange.value);
  }
</script>

{#if scouterEnabled || mockMode}
  <div class="mx-auto w-full max-w-screen-3xl px-4 py-4 sm:px-6 lg:px-8 space-y-6">
    <div
      class="flex flex-col xl:flex-row items-start xl:items-center justify-between gap-4 bg-white p-4 border-2 border-black shadow rounded-base"
    >
      <div class="flex items-center gap-3">
        <div class="p-2 bg-primary-100 border-2 border-black rounded-base shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
          <Sparkles class="w-6 h-6 text-black" />
        </div>
        <div>
          <h1 class="text-xl font-black text-black uppercase tracking-tight">
            GenAI Dashboard
          </h1>
          <p class="text-xs text-primary-600 font-mono mt-0.5">{subtitle}</p>
        </div>
      </div>

      {#if timeRangeState.selectedTimeRange}
        <DashboardTimeBar
          selectedRange={timeRangeState.selectedTimeRange}
          refreshing={timeRangeState.isRefreshing}
          onRangeChange={handleRangeChange}
          onRefresh={() => timeRangeState.refresh()}
        />
      {/if}
    </div>

    {@render children()}
  </div>
{:else}
  <ScouterRequiredView
    featureName="GenAI Dashboard"
    featureDescription="Track GenAI token usage, cost, latency, and tool calls with real-time observability powered by Scouter."
    icon={Sparkles}
  />
{/if}
