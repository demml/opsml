<script lang="ts">
  import {
    type CardRequest,
    type CardResponse,
    type Message,
    type MessageThread,
  } from "$lib/scripts/types";
  import { getToastStore, type ToastSettings } from '@skeletonlabs/skeleton';
  import { listCards, getMessages, putMessage } from "$lib/scripts/utils";
  import { onMount, afterUpdate } from "svelte";
  import { faPaperPlane } from '@fortawesome/free-solid-svg-icons'
  import Fa from 'svelte-fa'
  import MessageComponent from "./MessageComponent.svelte";


  const toastStore = getToastStore();

  export let registry: string
  export let repository: string;
  export let name: string;
  export let version: string;


  let currentMessage = '';
  let userName = ''; // New variable for user's name
  let messages: MessageThread = [];
  let uid: string;
  let textareaElement: HTMLTextAreaElement;
  let element;

  const cardReq: CardRequest = {
      name,
      repository,
      version,
      registry_type: registry,
    };

  
  function adjustTextareaHeight() {
    if (textareaElement) {
      // Reset height to auto to get the correct scrollHeight
      textareaElement.style.height = 'auto';
      // Set the height to the scrollHeight
      textareaElement.style.height = `${textareaElement.scrollHeight}px`;
    }
  }

  async function getThreadMessages():  Promise<MessageThread> {
    const cards: CardResponse = await listCards(cardReq);
    const selectedCard = cards.cards[0];
    uid = selectedCard.uid;

    return getMessages(selectedCard.uid, registry);
  }

  function addMessage(): void {

    if ( currentMessage === '' || userName === '') {

      const t: ToastSettings = {
          message: "message or user name is empty",
      };
      toastStore.trigger(t);


      return;
    }

		let message: Message = {
      uid,
      registry,
      user: userName,
      content: currentMessage,
      votes: 0,
      message_id: null,
      created_at: null,
      parent_id: null,
    };

    // insert the message into the thread
    putMessage(message)?.then(() => {
      currentMessage = '';
    });

    // update the thread with latest messages
    getThreadMessages()?.then((thread) => {
      messages = thread;
    });

    scrollToBottom(element);
		
	}

  function onPromptKeydown(event: KeyboardEvent): void {
		if (['Enter'].includes(event.code)) {
			event.preventDefault();
			addMessage();
		}
	}

  function timestampToLocalTime(timestamp: number): string {
    return new Date(timestamp * 1000).toLocaleDateString('en-US');
  }

  

  const scrollToBottom = async (node) => {
    node.scroll({ top: node.scrollHeight, behavior: 'smooth' });
  };


  onMount(async () => {
    messages = await getThreadMessages();
    if (textareaElement) {
      adjustTextareaHeight();
    }
    scrollToBottom(element);
  });

  // Either afterUpdate()
	afterUpdate(() => {
		if(messages) scrollToBottom(element);
  });



</script>


<div bind:this={element} class="max-h-[600px] overflow-y-auto pb-4 pt-8">
	{#each messages as message, index}
    <MessageComponent 
      message={message.message}
      index={index}
     />
  {/each}
</div>



<svg class="mr-1.5" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" focusable="false" role="img" width="1em" height="1em" preserveAspectRatio="xMidYMid meet" viewBox="0 0 32 32"><path d="M2 26h28v2H2z" fill="currentColor"></path><path d="M3,260 L24,260 L24,258.010742 L3,258.010742 L3,260 Z M13.3341,254.032226 L9.3,254.032226 L9.3,249.950269 L19.63095,240 L24,244.115775 L13.3341,254.032226 Z" fill="currentColor"></path></svg>

<div class="grid grid-row-2">

  <div class="grid grid-cols-1 grid-flow-col space-y-2 bg-surface-200 rounded-2xl mb-2">
    <input
      bind:value={userName}
      class="bg-transparent focus:ring-0 focus-visible:outline-none border-0 rounded-container-token"
      type="text"
      placeholder="Enter your name"
    />
  </div>

  <div class="grid grid-cols-1 grid-flow-col bg-surface-200 rounded-2xl focus-visible:outline-none">
    <textarea
      bind:value={currentMessage}
      class="bg-transparent focus:ring-0 focus-visible:outline-none border-0 rounded-container-token "
      name="prompt"
      id="prompt"
      placeholder="Write a message..."
      rows="2"
      on:keydown={onPromptKeydown}
      on:input={adjustTextareaHeight}
    ></textarea>
    <button class='input-group-shim justify-center p-2 bg-transparent bg-surface-200' on:click={addMessage}>
      <Fa class="bg-transparent" icon={faPaperPlane} color="#4b3978"/>
    </button>
  </div>

</div>

