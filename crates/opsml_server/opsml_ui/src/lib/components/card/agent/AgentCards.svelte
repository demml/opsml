<script lang="ts">
  import { Table } from 'lucide-svelte';
  import CardButton from '../service/CardButton.svelte';
  import { getRegistryFromString, RegistryType } from '$lib/utils';
  import type { Card } from '$lib/components/card/card_interfaces/servicecard';

  let { cards } = $props<{ cards: Card[] }>();

  const badgeColor = "#40328b";
  const iconColor = "#40328b";
</script>

<div class="rounded-lg border-2 border-black shadow-small bg-surface-50 p-4">
  <div class="flex items-center gap-2 mb-4 pb-3 border-b-2 border-black">
    <div class="p-2 bg-primary-100 rounded-lg border-2 border-black">
      <Table class="w-5 h-5 text-primary-800" />
    </div>
    <h3 class="text-lg font-bold text-primary-950">Associated Cards</h3>
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
