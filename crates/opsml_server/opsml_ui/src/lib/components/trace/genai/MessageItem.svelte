<script lang="ts">
  import {
    extractMessageRole,
    extractMessageText,
    type ChatMessage,
    type MessageRole,
  } from './messageFormat';

  let { message }: { message: ChatMessage } = $props();

  const role = $derived<MessageRole>(extractMessageRole(message));
  const text = $derived(extractMessageText(message));

  const roleClasses: Record<MessageRole, string> = {
    system: 'bg-surface-200 text-primary-800',
    user: 'bg-surface-100 text-primary-800',
    assistant: 'bg-primary-500 text-surface-50',
    tool: 'bg-surface-200 text-primary-700',
    developer: 'bg-surface-200 text-primary-800',
    function: 'bg-surface-200 text-primary-700',
  };
</script>

<div class="border-2 border-black bg-surface-50 p-2">
  <div class="flex items-center gap-2 mb-2">
    <span class="text-[10px] uppercase font-black px-1.5 py-0.5 border-2 border-black {roleClasses[role]}">
      {role}
    </span>
    {#if message.name}
      <span class="text-[10px] uppercase font-black text-primary-700">{message.name}</span>
    {/if}
    {#if message.tool_call_id}
      <span class="text-[10px] uppercase font-black text-primary-700 font-mono">{message.tool_call_id}</span>
    {/if}
  </div>
  <pre class="text-xs font-mono whitespace-pre-wrap break-words text-primary-900">{text}</pre>
</div>
