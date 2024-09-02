<script lang="ts">

  import { type PaginationSettings } from '@skeletonlabs/skeleton';
  import { type CardResponse } from "$lib/scripts/types";
  import Versions from '$lib/card/Versions.svelte';


  /** @type {import('./$types').PageData} */
  export let data;

  let cards: CardResponse = data.cards;

  let registry: string = data.registry;

  let repository: string= data.repository;

  let name: string = data.name;

  let artifactSearchTerm: string | undefined = undefined;

  let paginationSettings = {
    page: 0,
    limit: 30,
    size: data.nbr_cards,
    amounts: [],
  } satisfies PaginationSettings;



</script>

<Versions 
  cards={cards} 
  registry={registry} 
  repository={repository} 
  name={name} 
  paginationSettings={paginationSettings} 
  artifactSearchTerm={artifactSearchTerm}
/>