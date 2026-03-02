<script lang="ts">
  import type { PromptCard } from '$lib/components/card/card_interfaces/promptcard';
  import CardReadMe from '$lib/components/card/CardReadMe.svelte';
  import NoReadme from '$lib/components/readme/NoReadme.svelte';
  import Metadata from '$lib/components/card/prompt/Metadata.svelte';
  import { MessageSquareText } from 'lucide-svelte';

  let { data } = $props();
  let card: PromptCard = data.metadata;
</script>


<div class="flex-1 mx-auto w-11/12 pt-6 px-4 pb-10">

  <!-- Hero Banner -->
  <div class="mb-8 border-2 border-black shadow bg-primary-100 p-5 flex flex-wrap items-center justify-between gap-4">
    <div class="flex items-center gap-4">
      <div class="p-3 bg-primary-500 border-2 border-black shadow-small rounded-base">
        <MessageSquareText class="w-7 h-7 text-white" />
      </div>
      <div>
        <div class="flex items-center gap-3 mb-1">
          <h1 class="text-2xl font-black text-black">{card.name}</h1>
          <span class="badge bg-primary-500 text-white border-2 border-black shadow-small text-xs font-black uppercase tracking-wider px-2 py-0.5">
            Prompt
          </span>
          <span class="badge bg-surface-50 text-primary-800 border-2 border-black shadow-small text-xs font-bold px-2 py-0.5">
            v{card.version}
          </span>
        </div>
        <p class="text-sm font-mono text-primary-700 font-bold">{card.space} · {card.uid}</p>
      </div>
    </div>
  </div>

  <!-- Main Content Grid -->
  <div class="grid grid-cols-1 gap-6 lg:grid-cols-3 lg:gap-8">

    <!-- README / Content -->
    <div class="lg:col-span-2">
      {#if data.readme.exists}
        <div class="rounded-base border-black border-2 shadow bg-surface-50 w-full">
          <CardReadMe
            name={card.name}
            space={card.space}
            registryType={data.registryType}
            version={card.version}
            readMe={data.readme}
          />
        </div>
      {:else}
        <div class="rounded-base border-2 border-black shadow bg-primary-100 w-full min-h-[200px] flex items-center justify-center">
          <NoReadme
            name={card.name}
            space={card.space}
            registryType={data.registryType}
            version={card.version}
          />
        </div>
      {/if}
    </div>

    <!-- Metadata Sidebar -->
    <div class="lg:col-span-1">
      <div class="rounded-base bg-surface-50 border-2 border-black shadow-primary p-4">
        <Metadata card={card} />
      </div>
    </div>

  </div>
</div>
