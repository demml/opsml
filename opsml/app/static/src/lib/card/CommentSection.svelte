<script lang="ts">
  import {
    type CardRequest,
    type CardResponse,
    type Comment,
  } from "$lib/scripts/types";
  import { listCards, getComments } from "$lib/scripts/utils";

  export let registry: string;
  export let repository: string;
  export let name: string;
  export let version: string;

  const cardReq: CardRequest = {
      name,
      repository,
      version,
      registry_type: registry,
    };

  async function getCardComments():  Promise<Comment[]> {
    const cards: CardResponse = await listCards(cardReq);
    const selectedCard = cards.cards[0];
    return getComments(selectedCard.uid, registry);
  }


</script>

{#await getCardComments()}
{:then comments}

  {#if comments.length === 0}
    <p>No comments yet</p>
  {:else}
    {#each comments as comment}
      <div class="bg-white dark:bg-surface-900 p-4 rounded-lg shadow-md my-4">
        <p>{comment.content}</p>
        <p class="text-sm text-gray-500 dark:text-gray-400">{comment.created_at}</p>
      </div>
    {/each}
  {/if}

{:catch error}
  <p>{error.message}</p>
{/await}

