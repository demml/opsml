<script lang="ts">
  
  import type { PageProps } from './$types';
  import PromptPage from '$lib/components/card/prompt/PromptPage.svelte';
  import ServicePage from '$lib/components/card/service/ServicePage.svelte';
  import { RegistryType } from '$lib/utils';
  import AgentPage from '$lib/components/card/agent/AgentPage.svelte';

  let { data }: PageProps = $props();
  let registryType = data.registryType;

</script>

{#if registryType === RegistryType.Prompt}
  <PromptPage {data} />
{:else if registryType === RegistryType.Mcp}
  <ServicePage {data} />
{:else if registryType === RegistryType.Agent}
  <AgentPage {data} />
{:else}
  <div class="mx-auto w-full max-w-8xl px-4 py-6 sm:px-6 lg:px-8">
    <div class="rounded-base border-black border-3 shadow bg-primary-100 w-full min-h-[200px] flex items-center justify-center">
      <p class="text-primary-800">Unknown registry type: {registryType}</p>
    </div>
  </div>
{/if}

