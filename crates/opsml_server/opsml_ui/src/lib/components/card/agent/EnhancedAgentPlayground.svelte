<script lang="ts">
  import { MessageSquare, Send, Loader2, Zap, ExternalLink, AlertCircle, CheckCircle } from 'lucide-svelte';
  import type { AgentSpec } from "./types";
  import { inferAgentContract, formatExamplesForDisplay } from './agentInference';
  import type { AgentContract, AgentSkillContract } from './agentInference';
  import { createAgentClient } from './agentClient';
  import type { AgentClient } from './agentClient';
  import AgentAuthConfig from './AgentAuthConfig.svelte';

  let {
    agentSpec,
    agentName,
    fullscreen = false
  } = $props<{
    agentSpec: AgentSpec;
    agentName: string;
    fullscreen?: boolean;
  }>();

  // Infer contract from agent spec
  let contract = $state<AgentContract>(inferAgentContract(agentSpec));
  let client = $state<AgentClient | null>(null);

  // Authentication state
  let authConfig = $state<Record<string, string>>({});
  let showAuthConfig = $state(false);

  // Skill selection
  let selectedSkill = $state<AgentSkillContract | null>(contract.skills[0] || null);
  
  // Message state
  let message = $state('');
  let messages = $state<Array<{
    role: 'user' | 'agent' | 'system';
    content: string;
    timestamp: Date;
    skillName?: string;
  }>>([]);
  
  let isLoading = $state(false);
  let streamingContent = $state('');
  let useStreaming = $state(false);

  // Error state
  let lastError = $state<string | null>(null);

  // Initialize client when auth config changes
  $effect(() => {
    if (Object.keys(authConfig).length > 0) {
      client = createAgentClient(contract, {
        authConfig,
        timeout: 30000,
        customHeaders: {
          'X-Agent-Name': agentName,
        },
      });
    }
  });

  // Check if auth is configured
  const isAuthConfigured = $derived(() => {
    const requiredSchemes = contract.security.requirements.flat();
    if (requiredSchemes.length === 0) return true; // No auth required
    return requiredSchemes.some(scheme => authConfig[scheme]);
  });

  // Check if skill supports streaming
  const canStream = $derived(() => {
    if (!selectedSkill) return false;
    return selectedSkill.endpoints.some(e => e.streaming) && contract.capabilities.streaming;
  });

  async function sendMessage() {
    if (!message.trim() || !selectedSkill || isLoading || !client) return;

    const userMessage = message.trim();
    message = '';
    lastError = null;

    messages = [...messages, {
      role: 'user',
      content: userMessage,
      timestamp: new Date(),
      skillName: selectedSkill.name,
    }];

    isLoading = true;
    streamingContent = '';

    try {
      if (useStreaming && canStream()) {
        // Streaming response
        messages = [...messages, {
          role: 'agent',
          content: '',
          timestamp: new Date(),
          skillName: selectedSkill.name,
        }];

        const streamGenerator = client.invokeSkillStream({
          skill: selectedSkill,
          task: userMessage,
        });

        let accumulatedContent = '';
        for await (const chunk of streamGenerator) {
          accumulatedContent += chunk.data;
          streamingContent = accumulatedContent;
          
          // Update last message with accumulated content
          messages = messages.map((msg, idx) =>
            idx === messages.length - 1
              ? { ...msg, content: accumulatedContent }
              : msg
          );

          if (chunk.done) break;
        }
      } else {
        // Non-streaming response
        const response = await client.invokeSkill({
          skill: selectedSkill,
          task: userMessage,
        });

        if (response.status === 'failed' && response.error) {
          lastError = response.error.message;
          messages = [...messages, {
            role: 'system',
            content: `❌ Error: ${response.error.message}`,
            timestamp: new Date(),
          }];
        } else {
          const content = typeof response.result === 'string'
            ? response.result
            : JSON.stringify(response.result, null, 2);

          messages = [...messages, {
            role: 'agent',
            content: content,
            timestamp: new Date(),
            skillName: selectedSkill.name,
          }];
        }
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      lastError = errorMessage;
      messages = [...messages, {
        role: 'system',
        content: `❌ Error: ${errorMessage}`,
        timestamp: new Date(),
      }];
    } finally {
      isLoading = false;
      streamingContent = '';
    }
  }

  function handleKeyPress(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  function useExample(example: string) {
    message = example;
  }

  function openAuthConfig() {
    showAuthConfig = true;
  }

  function closeAuthConfig() {
    showAuthConfig = false;
  }

  const statusBadge = $derived(() => {
    if (isAuthConfigured()) {
      return {
        icon: CheckCircle,
        text: 'Ready',
        color: 'bg-secondary-300 text-secondary-950 border-secondary-950',
      };
    } else {
      return {
        icon: AlertCircle,
        text: 'Auth Required',
        color: 'bg-warning-300 text-warning-950 border-warning-950',
      };
    }
  });
</script>

{#if showAuthConfig}
  <AgentAuthConfig
    securitySchemes={contract.security.schemes}
    {authConfig}
    onClose={closeAuthConfig}
    onSave={(newConfig) => {
      authConfig = newConfig;
      closeAuthConfig();
    }}
  />
{/if}

<div class="rounded-lg border-2 border-black shadow-small bg-surface-50 flex flex-col {fullscreen ? 'h-screen' : 'mx-auto w-11/12 my-6 min-h-[600px]'}">
  
  <!-- Header -->
  <div class="flex items-center justify-between gap-2 p-4 pb-3 border-b-2 border-black bg-gradient-primary">
    <div class="flex items-center gap-2">
      <div class="p-2 bg-white rounded-lg border-2 border-black shadow-small">
        <Zap class="w-5 h-5 text-primary-800" />
      </div>
      <div>
        <h3 class="text-lg text-primary-800 font-bold">Agent Playground</h3>
        <p class="text-xs text-primary-800">{agentName}</p>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <!-- Status Badge -->
      {#if true}
        {@const StatusIcon = statusBadge().icon}
        <div class="flex items-center gap-1 px-2 py-1 rounded-lg border-2 border-black shadow-small {statusBadge().color}">
          <StatusIcon class="w-3 h-3" />
          <span class="text-xs font-bold">{statusBadge().text}</span>
        </div>
      {/if}

      <button
        onclick={openAuthConfig}
        class="text-black px-3 py-1 text-xs bg-white rounded-lg border-2 border-black shadow-small hover:shadow-hover transition-all font-bold"
      >
        Configure Auth
      </button>
    </div>
  </div>

  <!-- Skill Selection -->
  {#if contract.skills.length > 1}
    <div class="p-3 border-b-2 border-black bg-surface-100">
      <label for="skill-select" class="text-xs font-bold text-gray-700 mb-1 block">Select Skill:</label>
      <div class="flex flex-wrap gap-2">
        {#each contract.skills as skill}
          <button
            onclick={() => selectedSkill = skill}
            class="px-3 py-1 text-xs rounded-lg border-2 border-black shadow-small transition-all {selectedSkill?.skillId === skill.skillId ? 'bg-primary-500 text-white font-bold' : 'bg-white text-gray-900 hover:bg-gray-100'}"
          >
            {skill.name}
          </button>
        {/each}
      </div>
    </div>
  {/if}

  <!-- Skill Info & Examples -->
  {#if selectedSkill}
    <div class="p-3 border-b-2 border-black bg-surface-50">
      <div class="flex flex-col sm:flex-row sm:items-start gap-3">
        <!-- Description -->
        <div class="flex-1 min-w-0">
          <p class="text-xs font-bold text-gray-700 mb-1">What this skill does:</p>
          <p class="text-sm text-gray-900">{selectedSkill.description}</p>
          
          <!-- Input/Output Modes -->
          <div class="flex flex-wrap gap-2 mt-2">
            {#each selectedSkill.inputModes as mode}
              <span class="inline-flex items-center rounded border-2 border-black shadow-small bg-tertiary-100 text-tertiary-950 px-2 py-0.5 text-xs">
                <span class="font-bold">Input:</span>
                <span class="ml-1">{mode}</span>
              </span>
            {/each}
            {#each selectedSkill.outputModes as mode}
              <span class="inline-flex items-center rounded border-2 border-black shadow-small bg-secondary-100 text-secondary-950 px-2 py-0.5 text-xs">
                <span class="font-bold">Output:</span>
                <span class="ml-1">{mode}</span>
              </span>
            {/each}
          </div>
        </div>

        <!-- Examples -->
        {#if selectedSkill.examples.length > 0}
          <div class="sm:w-64">
            <p class="text-xs font-bold text-gray-700 mb-1">Try these examples:</p>
            <div class="space-y-1">
              {#each formatExamplesForDisplay(selectedSkill.examples) as example}
                <button
                  onclick={() => useExample(example.value)}
                  class="text-black w-full text-left px-2 py-1 text-xs bg-white rounded border-2 border-black hover:bg-primary-50 transition-colors"
                >
                  {example.value}
                </button>
              {/each}
            </div>
          </div>
        {/if}
      </div>

      <!-- Streaming Toggle -->
      {#if canStream()}
        <div class="mt-3 flex items-center gap-2">
          <input
            type="checkbox"
            id="streaming-toggle"
            bind:checked={useStreaming}
            class="rounded border-2 border-black"
          />
          <label for="streaming-toggle" class="text-xs text-gray-700 cursor-pointer">
            Enable streaming (real-time responses)
          </label>
        </div>
      {/if}
    </div>
  {/if}

  <!-- Error Display -->
  {#if lastError}
    <div class="mx-4 mt-3 p-3 bg-error-100 border-2 border-error-600 rounded-lg">
      <div class="flex items-start gap-2">
        <AlertCircle class="w-4 h-4 text-error-800 flex-shrink-0 mt-0.5" />
        <div class="flex-1 min-w-0">
          <p class="text-xs font-bold text-error-900">Error</p>
          <p class="text-xs text-error-800">{lastError}</p>
        </div>
      </div>
    </div>
  {/if}

  <!-- Messages -->
  <div class="flex-1 min-h-0 overflow-y-auto p-4 space-y-3">
    {#if messages.length === 0}
      <div class="flex flex-col items-center justify-center h-full text-gray-500">
        <MessageSquare class="w-16 h-16 mb-3 opacity-30" />
        <p class="text-sm font-bold">Start a conversation with {agentName}</p>
        <p class="text-xs mt-1">
          {isAuthConfigured() ? 'Type a message below to get started' : 'Configure authentication first'}
        </p>
      </div>
    {:else}
      {#each messages as msg}
        <div class="flex {msg.role === 'user' ? 'justify-end' : 'justify-start'}">
          <div class="max-w-[80%]">
            <div class="text-xs text-gray-500 mb-1 {msg.role === 'user' ? 'text-right' : 'text-left'}">
              {msg.role === 'user' ? 'You' : msg.role === 'system' ? 'System' : agentName}
              {#if msg.skillName}
                • <span class="italic">{msg.skillName}</span>
              {/if}
              • {msg.timestamp.toLocaleTimeString()}
            </div>
            <div class="p-3 rounded-lg border-2 border-black shadow-small {msg.role === 'user' ? 'bg-primary-100' : msg.role === 'system' ? 'bg-warning-100' : 'bg-white'} whitespace-pre-wrap">
              <p class="text-sm">{msg.content}</p>
            </div>
          </div>
        </div>
      {/each}

      {#if isLoading}
        <div class="flex justify-start">
          <div class="max-w-[80%]">
            <div class="text-xs text-gray-500 mb-1">
              {agentName} is {useStreaming ? 'streaming' : 'processing'}...
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
        placeholder={isAuthConfigured() ? "Type your message... (Enter to send, Shift+Enter for new line)" : "Configure authentication first"}
        disabled={!selectedSkill || isLoading || !isAuthConfigured()}
        rows="2"
        class="text-black flex-1 px-3 py-2 border-2 border-black rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
      ></textarea>

      <button
        onclick={sendMessage}
        disabled={!message.trim() || !selectedSkill || isLoading || !isAuthConfigured()}
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
