<script lang="ts">
  import { Table } from 'lucide-svelte';
  import CardButton from '../service/CardButton.svelte';
  import { getRegistryFromString, RegistryType } from '$lib/utils';
  import type { Card } from '$lib/components/card/card_interfaces/servicecard';

  let { cards } = $props<{ cards: Card[] }>();

  const badgeColor = "currentColor";
  const iconColor = "currentColor";
</script>

<div class="rounded-base border-2 border-black shadow bg-surface-50 p-4">
  <div class="flex items-center gap-2 mb-4 pb-3 border-b-2 border-black">
    <div class="p-1.5 bg-primary-500 border-2 border-black rounded-base">
      <Table class="w-4 h-4 text-white" />
    </div>
    <h3 class="text-sm font-black text-primary-950 uppercase tracking-wide">Associated Cards</h3>
    <span class="badge bg-primary-100 text-primary-800 border border-black text-xs font-bold shadow-small px-2">{cards.length}</span>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
    {#each cards as card}
      <CardButton
        iconColor={iconColor}
        badgeColor={badgeColor}
        name={card.name}
        space={card.space}
        version={card.version}
        registry={getRegistryFromString(card.registry_type) || RegistryType.Model}
        alias={card.alias}
      />
    {/each}
  </div>
</div>
