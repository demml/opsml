<script lang="ts">

  import Homepage from "$lib/components/home/Homepage.svelte";
  import type { RecentCards } from "$lib/components/home/utils";
  import type { PageProps } from './$types';

  let { data }: PageProps = $props();
  let cards: RecentCards  = data.cards;

</script>
  
<Homepage {cards} />

