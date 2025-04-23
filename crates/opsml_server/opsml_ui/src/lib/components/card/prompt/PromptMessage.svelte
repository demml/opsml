<script lang="ts">
  import Pill from "$lib/components/utils/Pill.svelte";
  import type { Message } from "./types";
  import { Trash2 } from 'lucide-svelte';
 

  let { 
    message = $bindable(),
    deleteCallback = $bindable(),
   } = $props<{
    message: Message;
    deleteCallback: (message: Message) => void;
   }>();

   

</script> 


<div class="w-full p-2 rounded-lg relative">
  <div class="flex justify-between items-center pb-2">
    <Pill key="role" value={message.role} />
    <button
      class="text-red-500 hover:text-red-700 rounded-full p-1 hover:bg-red-100 transition-colors"
      onclick={deleteCallback}
      title="Delete message"
    >
      <Trash2 color="#f54c54" />
    </button>
  </div>

  <textarea
    class="w-full rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 focus-visible:ring-2 focus-visible:ring-primary-800"
    bind:value={message.content.Str}
  > 
  </textarea>

</div>



