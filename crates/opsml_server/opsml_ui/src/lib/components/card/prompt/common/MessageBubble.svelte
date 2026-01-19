<script lang="ts">
  import type { MessageNum } from '$lib/components/genai/provider/types';
  import { Provider, isOpenAIMessage } from '$lib/components/genai/types';
  import ContentRenderer from './ContentRenderer.svelte';
  import { User, Cpu, Terminal, Wrench } from 'lucide-svelte';

  let { message, provider, index } = $props<{ 
    message: MessageNum; 
    provider: Provider;
    index?: number;
  }>();

  // Normalize Role Extraction
  let role = $derived.by(() => {
    if (isOpenAIMessage(message)) return message.role;
    if ('role' in message) return message.role;
    // Anthropic TextBlockParam (used in System) doesn't have a role, imply System
    return 'system';
  });

  // Dynamic Styling based on Role
  let roleStyles = $derived.by(() => {
    switch (role) {
      case 'user': return { 
        bg: 'bg-white', 
        border: 'border-black',
        badge: 'bg-primary-300',
        icon: User 
      };
      case 'system': return { 
        bg: 'bg-surface-50', 
        border: 'border-black', // Distinct style for system
        badge: 'bg-red-300',
        icon: Terminal
      };
      case 'assistant': 
      case 'model': return { 
        bg: 'bg-green-50', 
        border: 'border-black',
        badge: 'bg-green-300',
        icon: Cpu
      };
      case 'tool': return {
        bg: 'bg-slate-100',
        border: 'border-black dashed',
        badge: 'bg-slate-300',
        icon: Wrench
      }
      default: return { 
        bg: 'bg-white', 
        border: 'border-black',
        badge: 'bg-gray-200',
        icon: Terminal 
      };
    }
  });
</script>

<div class={`flex flex-col w-full rounded-base border-2 ${roleStyles.border} shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] overflow-hidden transition-transform hover:-translate-y-0.5`}>
  
  <div class={`flex flex-row justify-between items-center px-3 py-2 border-b-2 border-black ${roleStyles.badge}`}>
    <div class="flex items-center gap-2">
      <roleStyles.icon class="w-4 h-4 text-black" />
      <span class="font-bold text-xs uppercase tracking-wider text-black">{role}</span>
    </div>
    {#if index !== undefined}
      <span class="text-[10px] font-mono font-bold bg-white/50 px-1.5 py-0.5 rounded border border-black/20 text-black">#{index + 1}</span>
    {/if}
  </div>

  <div class={`p-4 ${roleStyles.bg}`}>
    <ContentRenderer {message} {provider} />
  </div>
</div>