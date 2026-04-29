<script lang="ts">

  import Homepage from "$lib/components/home/Homepage.svelte";
  import type { HomePageStats, RecentCards } from "$lib/components/home/utils.server";
  import type { PageProps } from './$types';

  let { data }: PageProps = $props();
  const emptyCards: RecentCards = {
    modelcards: [],
    datacards: [],
    experimentcards: [],
    promptcards: [],
  };
  let cards: RecentCards = Array.isArray(data.cards) ? emptyCards : data.cards;
  let stats: HomePageStats = data.stats;

</script>

<Homepage {cards} {stats} />
