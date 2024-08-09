<script lang="ts">
  import {
    type Message,
  } from "$lib/scripts/types";
  import { faEdit, faTrash, faReply } from '@fortawesome/free-solid-svg-icons'
  import Fa from 'svelte-fa'
  import { popup, type PopupSettings } from '@skeletonlabs/skeleton';

  const popupEditHover: PopupSettings = {
    event: 'hover',
    target: 'popupEditHover',
    placement: 'top'
  };

  const popupReplyHover: PopupSettings = {
    event: 'hover',
    target: 'popupReplyHover',
    placement: 'top'
  };

  const popupDeleteHover: PopupSettings = {
    event: 'hover',
    target: 'popupDeleteHover',
    placement: 'top'
  };

  function timestampToLocalTime(timestamp: number): string {
    return new Date(timestamp * 1000).toLocaleDateString('en-US');
  }

  function editHandler() {
    if (isEditing) {
      currentText = message.content;
    }
    isEditing = !isEditing;
  }

  export let message: Message;
  export let index: number;
  let isEditing: boolean = false;
  let currentText: string = message.content;

</script>

<div class="card p-2 bg-primary-500 text-white text-xs" data-popup="popupEditHover">
	<p>Edit</p>
	<div class="arrow variant-filled-primary" />
</div>

<div class="card p-2 bg-primary-500 text-white text-xs" data-popup="popupReplyHover">
	<p>Reply</p>
	<div class="arrow variant-filled-primary" />
</div>

<div class="card p-2 bg-primary-500 text-white text-xs" data-popup="popupDeleteHover">
	<p>Delete</p>
	<div class="arrow variant-filled-primary" />
</div>
  
  <div class="text-wrap my-2 p-4 {index % 2 === 0 ? 'variant-soft' : 'bg-primary-50'} rounded-xl space-y-2">

    <div class="flex flex-row justify-between">

      <div>
        <header class="flex flex-row justify-start items-center space-x-1">
          <p class="font-bold text-primary-500">{message.user}</p>
          <small class="opacity-50 text-primary-500">@ {message.created_at ? timestampToLocalTime(message.created_at) : ''}</small>
        </header>
      </div>

      <div class="flex flex-row items-center gap-2">
        <div class="flex flex-row items-center">
          <button use:popup={popupEditHover} on:click={editHandler} class="text-sm text-gray pr-1">
            <Fa icon={faEdit} color="#4b3978"/>
          </button>
        </div>  

        <div class="flex flex-row items-center">
          <button use:popup={popupDeleteHover} class="text-sm text-gray pr-1">
            <Fa icon={faTrash} color="#4b3978"/>
          </button>
        </div>

        <div class="flex flex-row items-center">
          <button use:popup={popupReplyHover} class="text-sm text-gray pr-1">
            <Fa icon={faReply} color="#4b3978"/>
          </button>
        </div>

      </div>
    </div>
    {#if isEditing}
      <textarea class="w-full h-24 p-2 border border-gray-300 rounded-lg focus:ring-0 focus-visible:outline-none" bind:value={currentText}></textarea>
      <div class="flex flex-row justify-end">
        <button class="btn btn-sm bg-primary-500 text-white" on:click={editHandler}>Save</button>
      </div>
    {:else}
      <div class="flex text-wrap">
        <p>{message.content}</p>
      </div>
    {/if}
   

  </div>
 
  
