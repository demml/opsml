<script lang="ts">
  import MessageItem from './MessageItem.svelte';
  import type { ChatMessage } from './messageFormat';

  let { messages }: { messages: ChatMessage[] } = $props();
</script>

<div class="flex flex-col gap-2">
  {#each messages as message, i (i)}
    <!-- index-keyed: list is render-once; revisit if streaming/reorder lands -->
    <MessageItem {message} />
  {/each}
</div>
