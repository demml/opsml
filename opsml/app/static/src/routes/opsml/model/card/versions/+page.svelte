<script lang="ts">

  import { Paginator, type PaginationSettings } from '@skeletonlabs/skeleton';
  import {type registryPage } from "$lib/scripts/types";
  import Card from "$lib/Card.svelte";
  import { type CardResponse, type CardRequest } from "$lib/scripts/types";
  import { getRegistryPage } from "$lib/scripts/registry_page";
  import Search from "$lib/Search.svelte";
  import { listCards } from "$lib/scripts/utils";
  import Versions from '$lib/card/Versions.svelte';

  let artifactSearchTerm: string | undefined = undefined;

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
/>