<!-- Message.svelte -->
<script lang="ts">
    import type { MessageWithReplies } from '$lib/scripts/types';
    import ReplyThread from './ReplyThread.svelte';
  
    export let message: MessageWithReplies;

    let showReplies = false;
  
    function toggleReplies() {
      showReplies = !showReplies;
    }
  </script>
  
  <div class="message">
    <div class="message-content">
      <strong>{message.message.user}</strong>
      <p>{message.message.content}</p>
      <small>{message.message.created_at?.toLocaleString()}</small>
    </div>
    {#if message.replies && message.replies.length > 0}
      <button on:click={toggleReplies}>
        {showReplies ? 'Hide' : 'Show'} {message.replies.length} {message.replies.length === 1 ? 'reply' : 'replies'}
      </button>
      {#if showReplies}
        <ReplyThread replies={message.replies} />
      {/if}
    {/if}
  </div>
  
  <style>
    .message {
      border: 1px solid #ccc;
      padding: 1rem;
      border-radius: 4px;
    }
  
    .message-content {
      margin-bottom: 0.5rem;
    }
  
    button {
      background: none;
      border: none;
      color: blue;
      cursor: pointer;
    }
  </style>