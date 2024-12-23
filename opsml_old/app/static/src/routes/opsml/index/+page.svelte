<script lang="ts">

  import Homepage from "$lib/Homepage.svelte";
  import { getRecentCards } from "$lib/scripts/homepage";

  const cards: any = getRecentCards();

</script>

<Homepage cards={cards} />
