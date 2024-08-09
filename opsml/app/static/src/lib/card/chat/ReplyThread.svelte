<!-- ReplyThread.svelte -->
<script lang="ts">
  import type { MessageWithReplies } from '$lib/scripts/types';

  export let replies: MessageWithReplies[];

</script>

<div class="reply-thread">
  {#each replies as reply (reply.message.message_id)}
    <div class="reply">
      <strong>{reply.message.user}</strong>
      <p>{reply.message.content}</p>
      <small>{reply.message.created_at?.toLocaleString()}</small>
    </div>
  {/each}
</div>

<style>
  .reply-thread {
    margin-left: 1rem;
    border-left: 2px solid #ccc;
    padding-left: 1rem;
  }

  .reply {
    margin-bottom: 0.5rem;
  }
</style>