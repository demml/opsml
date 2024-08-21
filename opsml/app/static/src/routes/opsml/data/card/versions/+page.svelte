<script lang="ts">

  import { type PaginationSettings } from '@skeletonlabs/skeleton';
  import { type CardResponse } from "$lib/scripts/types";
  import Versions from '$lib/card/Versions.svelte';


  /** @type {import('./$types').PageData} */
  export let data;

  let cards: CardResponse;
  $: cards = data.cards;

  let activePage: number = 0;

  let registry: string;
  $: registry = data.registry;

  let repository: string;
  $: repository = data.repository;

  let name: string;
  $: name = data.name;

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