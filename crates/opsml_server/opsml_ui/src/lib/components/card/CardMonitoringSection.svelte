<script lang="ts">
  import { goto } from '$app/navigation';
  import { ExternalLink, ChevronDown, ChevronUp } from 'lucide-svelte';
  import { DriftType } from '$lib/components/scouter/types';
  import type { DriftProfile } from '$lib/components/scouter/types';
  
  // Import your existing monitoring components
  import CustomDashboard from '$lib/components/scouter/custom/CustomDashboard.svelte';
  import GenAIDashboard from '$lib/components/scouter/genai/dashboard/GenAIDashboard.svelte';
  import PsiDashboard from '$lib/components/scouter/psi/PsiDashboard.svelte';
  import SpcDashboard from '$lib/components/scouter/spc/SpcDashboard.svelte';

  let {
    cardData,
    driftType
  }: {
    cardData: any;
    driftType: DriftType;
  } = $props();

  let isExpanded = $state(true);
  
  // Filter profiles for the selected drift type
  let relevantProfiles = $derived(
    cardData.profiles.filter((p: DriftProfile) => 
      p.drift_type.toLowerCase() === driftType.toLowerCase()
    )
  );
  
  let selectedProfile = $state(relevantProfiles[0]?.name);
  
  let currentProfile = $derived(
    relevantProfiles.find((p: DriftProfile) => p.name === selectedProfile) || relevantProfiles[0]
  );

  function navigateToFullView() {
    const path = `/opsml/${cardData.registryType.toLowerCase()}/card/${cardData.space}/${cardData.name}/${cardData.version}/monitoring/${driftType.toLowerCase()}`;
    goto(path);
  }
</script>

<div class="border-3 border-black rounded-xl shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] bg-white overflow-hidden">
  <!-- Card header -->
  <div class="bg-primary-100 border-b-3 border-black p-4">
    <div class="flex items-center justify-between">
      <div class="flex-1 min-w-0">
        <h3 class="text-lg font-bold text-black truncate">
          {cardData.name}
        </h3>
        <p class="text-sm text-gray-600 font-medium">
          {cardData.space} · v{cardData.version}
        </p>
      </div>

      <div class="flex items-center gap-2">
        {#if relevantProfiles.length > 1}
          <select
            bind:value={selectedProfile}
            class="px-3 py-1.5 text-sm font-bold border-2 border-black rounded-lg bg-white shadow-small hover:shadow-none transition-shadow"
          >
            {#each relevantProfiles as profile}
              <option value={profile.name}>{profile.name}</option>
            {/each}
          </select>
        {/if}

        <button
          onclick={navigateToFullView}
          class="p-2 border-2 border-black rounded-lg bg-white shadow-small hover:shadow-none transition-shadow"
          title="Open full dashboard"
        >
          <ExternalLink class="w-4 h-4" />
        </button>

        <button
          onclick={() => isExpanded = !isExpanded}
          class="p-2 border-2 border-black rounded-lg bg-white shadow-small hover:shadow-none transition-shadow"
          title={isExpanded ? 'Collapse' : 'Expand'}
        >
          {#if isExpanded}
            <ChevronUp class="w-4 h-4" />
          {:else}
            <ChevronDown class="w-4 h-4" />
          {/if}
        </button>
      </div>
    </div>
  </div>

  <!-- Dashboard content -->
  {#if isExpanded && currentProfile}
    <div class="p-4">
      {#if driftType === DriftType.Custom}
        <CustomDashboard profile={currentProfile} compact={true} />
      {:else if driftType === DriftType.GenAI}
        <GenAIDashboard profile={currentProfile} compact={true} />
      {:else if driftType === DriftType.Psi}
        <PsiDashboard profile={currentProfile} compact={true} />
      {:else if driftType === DriftType.Spc}
        <SpcDashboard profile={currentProfile} compact={true} />
      {/if}
    </div>
  {/if}
</div>