<script lang="ts">

import { Paginator, type PaginationSettings } from '@skeletonlabs/skeleton';
import Card from "$lib/Card.svelte";
import { type CardResponse, type CardRequest } from "$lib/scripts/types";
import Search from "$lib/Search.svelte";
import { listCards } from "$lib/scripts/utils";

export let cards: CardResponse;
export let registry: string;
export let repository: string;
export let name: string;
export let paginationSettings: PaginationSettings;
export let artifactSearchTerm: string | undefined = undefined;

async function onPageChange(e: CustomEvent) {
    let page = e.detail;
    
    let cardReq: CardRequest = {
      name: name,
      repository: repository,
      version: artifactSearchTerm,
      registry_type: registry,
      page: page,

    };

    cards = await listCards(cardReq);
    paginationSettings.page = page;

  }

  function delay(fn, ms: number) {
    let timer = 0
    return function(...args) {
      clearTimeout(timer)

      // @ts-ignore
      timer = window.setTimeout(fn.bind(this, ...args), ms || 0)
    }
  }

  const searchVersions = async function () {

    let cardReq: CardRequest = {
    name: name,
    repository: repository,
    version: artifactSearchTerm,
    registry_type: registry,

    };

    cards = await listCards(cardReq);
  }

</script>


<div class="flex justify-center">
  <div class="flex-auto w-64 px-48 bg-white dark:bg-surface-900 min-h-screen">

    <div class="grid grid-cols-2 place-items-center pt-8">
      <div class="col-span-2 md:w-1/3">
        <Search bind:searchTerm={artifactSearchTerm} on:keydown={delay(searchVersions, 1000)} placeholder="Filter versions"/>
      </div>
    </div>

    <div class="pt-3 place-items-center grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">

      {#each cards.cards as card}
        <Card
          hoverColor="hover:text-secondary-500"
          hoverBorderColor="hover:border-secondary-500"
          repository= {repository}
          name= {name}
          version= {card.version}
          timestamp= {card.timestamp}
          svgClass="flex-none w-3 mr-0.5 fill-secondary-500 dark:fill-secondary-500"
          registry= {registry}
        />
      {/each}
    </div>
    <div class="pt-8 flex items-center">
      <div class="flex-1 mb-12 w-64 content-center">
        <Paginator
          bind:settings={paginationSettings}
          showFirstLastButtons="{true}"
          showPreviousNextButtons="{true}"
          justify="justify-center"
          on:page={onPageChange}
        />
      </div>
    </div>
  </div>
</div>
