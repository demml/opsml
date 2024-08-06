<script lang="ts">
  import {
    type CardRequest,
    type CardResponse,

    type MessageThread,
  } from "$lib/scripts/types";
  import MessageComponent from "./MessageComponent.svelte";
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

  async function getMessages():  Promise<MessageThread> {
    const cards: CardResponse = await listCards(cardReq);
    const selectedCard = cards.cards[0];
    return getComments(selectedCard.uid, registry);
  }


</script>

{#await getMessages()}
{:then messages}

  {#if messages.length === 0}
    <p>No messages yet</p>
  {:else}
    <div class="chat-thread">
      {#each messages as message (message.message.message_id)}
        <MessageComponent {message} />
      {/each}
    </div>
  {/if}

{:catch error}
  <p>{error.message}</p>
{/await}

