<script lang="ts">
  import { MessageSquare, Send, Loader2, Terminal, Settings } from 'lucide-svelte';
  import type { AgentInterface } from "./types";
  import AgentConfigSidebar from './AgentConfigSidebar.svelte';

  let { interfaces, agentName, fullscreen = false } = $props<{
    interfaces: AgentInterface[];
    agentName: string;
    fullscreen?: boolean;
  }>();

  let message = $state('');
  let messages = $state<Array<{ role: 'user' | 'agent'; content: string; timestamp: Date }>>([]);
  let isLoading = $state(false);
  let selectedInterface = $state<AgentInterface | null>(interfaces[0] || null);
  let showConfig = $state(false);

  // Configuration state
  let config = $state({
    endpoint: '',
    method: 'POST',
    headers: '{\n  "Content-Type": "application/json",\n  "Authorization": "Bearer YOUR_TOKEN"\n}',
    params: '{\n  "temperature": 0.7,\n  "max_tokens": 1000\n}',
    timeout: 30000
  });

  // Update endpoint when interface changes
  $effect(() => {
    if (selectedInterface) {
      config.endpoint = selectedInterface.url;
    }
  });

  async function sendMessage() {
    if (!message.trim() || !selectedInterface || isLoading) return;

    const userMessage = message.trim();
    message = '';

    messages = [...messages, { role: 'user', content: userMessage, timestamp: new Date() }];
    isLoading = true;

    try {
      // Placeholder for actual API call
      // In production, this would call the agent's endpoint with the configured settings
      await new Promise(resolve => setTimeout(resolve, 1000));

      const configSummary = `Endpoint: ${config.endpoint}\nMethod: ${config.method}\nTimeout: ${config.timeout}ms`;
      messages = [...messages, {
        role: 'agent',
        content: `🚧 Agent interaction coming soon!\n\nYour message: "${userMessage}"\n\n${configSummary}`,
        timestamp: new Date()
      }];
    } catch (error) {
      messages = [...messages, {
        role: 'agent',
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date()
      }];
    } finally {
      isLoading = false;
    }
  }

  function handleKeyPress(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  function openConfig() {
    showConfig = true;
  }

  function closeConfig() {
    showConfig = false;
  }

  const configSummary = $derived(() => {
    const summary: Array<{ label: string; value: string }> = [
      { label: 'Method', value: config.method },
      { label: 'Timeout', value: `${config.timeout}ms` },
    ];

    // Try to parse headers and show count
    try {
      const headers = JSON.parse(config.headers);
      const headerCount = Object.keys(headers).length;
      if (headerCount > 0) {
        summary.push({ label: 'Headers', value: `${headerCount} configured` });
      }
    } catch {
      // Invalid JSON, skip
    }

    // Try to parse params and show key ones
    try {
      const params = JSON.parse(config.params);
      if (params.temperature !== undefined) {
        summary.push({ label: 'Temperature', value: String(params.temperature) });
      }
      if (params.max_tokens !== undefined) {
        summary.push({ label: 'Max Tokens', value: String(params.max_tokens) });
      }
    } catch {
      // Invalid JSON, skip
    }

    return summary;
  });
</script>

{#if showConfig}
  <AgentConfigSidebar {config} onClose={closeConfig} />
{/if}

<div class="rounded-lg border-2 border-black shadow-small bg-surface-50 flex flex-col mx-auto w-11/12 my-6 pb-2">
  <div class="flex items-center justify-between gap-2 p-4 pb-3 border-b-2 border-black bg-gradient-primary">
    <div class="flex items-center gap-2">
      <div class="p-2 bg-white rounded-lg border-2 border-black shadow-small">
        <MessageSquare class="w-5 h-5 text-primary-800" />
      </div>
      <div>
        <h3 class="text-lg text-primary-800 font-bold">Agent Playground</h3>
        <p class="text-xs text-primary-800">{agentName}</p>
      </div>
    </div>

    <div class="flex items-center gap-2">
      {#if interfaces.length > 1}
        <select
          bind:value={selectedInterface}
          class="text-xs border-2 border-black rounded px-2 py-1 bg-white"
        >
          {#each interfaces as iface}
            <option value={iface}>
              {iface.url}
            </option>
          {/each}
        </select>
      {/if}

      <button
        onclick={openConfig}
        class="p-2 bg-white rounded-lg border-2 border-black shadow-small hover:shadow-hover transition-all"
        aria-label="Open configuration"
      >
        <Settings class="w-4 h-4 text-primary-800" />
      </button>
    </div>
  </div>

  <!-- Configuration Summary -->
  <div class="px-4 pt-3 pb-2 border-b-2 border-black bg-surface-50">
    <div class="flex flex-col gap-2">
      <!-- Endpoint -->
      <div class="flex items-center gap-2">
        <span class="text-xs font-bold text-gray-700">Endpoint:</span>
        <span class="text-xs font-mono text-gray-900 truncate flex-1">{config.endpoint || 'Not configured'}</span>
      </div>

      <!-- Config Pills -->
      <div class="flex flex-wrap gap-1">
        {#each configSummary() as item}
          <span class="inline-flex items-center rounded-lg border-2 border-black shadow-small bg-primary-100 text-primary-900 px-2 py-0.5 text-xs">
            <span class="font-bold">{item.label}:</span>
            <span class="ml-1">{item.value}</span>
          </span>
        {/each}
      </div>
    </div>
  </div>

  <!-- Coming Soon Notice -->
  <div class="p-4 bg-warning-100 border-b-2 border-black">
    <div class="flex items-start gap-2">
      <Terminal class="w-5 h-5 text-warning-800 flex-shrink-0 mt-0.5" />
      <div>
        <p class="text-sm font-bold text-warning-900">Interactive Agent Playground - Coming Soon!</p>
        <p class="text-xs text-warning-800 mt-1">
          This interface will allow you to interact with your agent in real-time. For now, you can test your agent using the API endpoint directly.
        </p>
      </div>
    </div>
  </div>

  <!-- Messages -->
  <div class="flex-1 min-h-0 overflow-y-auto p-4 space-y-3">
    {#if messages.length === 0}
      <div class="flex flex-col items-center justify-center h-full text-gray-500">
        <MessageSquare class="w-16 h-16 mb-3 opacity-30" />
        <p class="text-sm font-bold">Start a conversation with {agentName}</p>
        <p class="text-xs mt-1">Type a message below to get started</p>
      </div>
    {:else}
      {#each messages as msg}
        <div class="flex {msg.role === 'user' ? 'justify-end' : 'justify-start'}">
          <div class="max-w-[80%]">
            <div class="text-xs text-gray-500 mb-1 {msg.role === 'user' ? 'text-right' : 'text-left'}">
              {msg.role === 'user' ? 'You' : agentName} • {msg.timestamp.toLocaleTimeString()}
            </div>
            <div class="p-3 rounded-lg border-2 border-black shadow-small {msg.role === 'user' ? 'bg-primary-100' : 'bg-white'} whitespace-pre-wrap">
              <p class="text-sm">{msg.content}</p>
            </div>
          </div>
        </div>
      {/each}

      {#if isLoading}
        <div class="flex justify-start">
          <div class="max-w-[80%]">
            <div class="text-xs text-gray-500 mb-1">
              {agentName} is typing...
            </div>
            <div class="p-3 rounded-lg border-2 border-black shadow-small bg-white flex items-center gap-2">
              <Loader2 class="w-4 h-4 animate-spin text-primary-600" />
              <span class="text-sm text-gray-600">Thinking...</span>
            </div>
          </div>
        </div>
      {/if}
    {/if}
  </div>

  <!-- Input -->
  <div class="p-4 border-t-2 border-black bg-surface-100">
    <div class="flex gap-2">
      <textarea
        bind:value={message}
        onkeydown={handleKeyPress}
        placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
        disabled={!selectedInterface || isLoading}
        rows="2"
        class="flex-1 px-3 py-2 border-2 border-black rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
      ></textarea>

      <button
        onclick={sendMessage}
        disabled={!message.trim() || !selectedInterface || isLoading}
        class="px-4 py-2 bg-primary-500 text-white font-bold rounded-lg border-2 border-black shadow-small hover:shadow-hover disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
      >
        {#if isLoading}
          <Loader2 class="w-4 h-4 animate-spin" />
        {:else}
          <Send class="w-4 h-4" />
        {/if}
      </button>
    </div>
  </div>
</div>
