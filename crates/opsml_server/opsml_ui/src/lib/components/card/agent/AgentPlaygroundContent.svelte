<script lang="ts">
  import { MessageSquare, Send, Loader2, Zap, AlertCircle, CheckCircle, X, Bug } from 'lucide-svelte';
  import type { AgentSpec, DebugPayload, ChatMessage, MessageRole } from "./types";
  import { isA2ATask, isA2AResponse, extractTextFromA2ATask, } from "./types";
  import { inferAgentContract, formatExamplesForDisplay, inferHealthEndpoint } from './agentInference';
  import type { AgentContract, AgentSkillContract } from './agentInference';
  import { createAgentClient } from './agentClient';
  import type { AgentClient } from './agentClient';
  import AgentAuthConfig from '$lib/components/card/agent/AgentAuthConfig.svelte';
  import DebugPayloadSidebar from './DebugPayloadSidebar.svelte';
  import { onMount, onDestroy } from 'svelte';
  import type { DeploymentConfig } from '$lib/components/card/card_interfaces/servicecard';



  let {
    agentSpec,
    agentName,
    onClose,
    deploymentConfig,
    showCloseButton = false,
  } = $props<{
    agentSpec: AgentSpec;
    agentName: string;
    onClose?: () => void;
    deploymentConfig?: DeploymentConfig[];
    showCloseButton?: boolean;
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
  let messages = $state<ChatMessage[]>([]);

  let isLoading = $state(false);
  let streamingContent = $state('');
  let useStreaming = $state(false);

  // Error state
  let lastError = $state<string | null>(null);

  // Debug sidebar state
  let showDebugSidebar = $state(false);
  let selectedDebugIndex = $state<number | null>(null);
  let isDebugClosing = $state(false);
  let isHealthy = $state<boolean>(false);
  let hasCheckedHealth = $state(false);

  interface DebugMessage {
    index: number;
    role: MessageRole;
    content: string;
    skillName?: string;
    timestamp: Date;
    debugPayload: DebugPayload;
  }

  const debugMessages = $derived(
    messages
      .map((msg, idx) => ({ ...msg, index: idx }))
      .filter((msg): msg is typeof msg & { debugPayload: DebugPayload } => (
        msg.debugPayload !== undefined && (msg.role === 'user' || msg.role === 'agent')
      ))
  );

  function openDebugSidebar() {
    // Auto-select the latest message with a debugPayload
    if (selectedDebugIndex === null && debugMessages.length > 0) {
      selectedDebugIndex = debugMessages[debugMessages.length - 1].index;
    }
    showDebugSidebar = true;
  }

  function closeDebugSidebar() {
    isDebugClosing = true;
    setTimeout(() => {
      showDebugSidebar = false;
      isDebugClosing = false;
      selectedDebugIndex = null;
    }, 20);
  }

  onMount(() => {
    if (showDebugSidebar) {
      document.body.style.overflow = 'hidden';
    }
  });

  onDestroy(() => {
    document.body.style.overflow = '';
  });

  $effect(() => {
    if (showDebugSidebar) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
  });

  // Initialize client - create it immediately if no auth required, or when auth config changes
  $effect(() => {
    const requiredSchemes = contract.security.requirements.flat();
    const noAuthRequired = requiredSchemes.length === 0;

    if (noAuthRequired || Object.keys(authConfig).length > 0) {
      client = createAgentClient(contract, {
        authConfig,
        timeout: 30000,
        customHeaders: {
          'X-Agent-Name': agentName,
        },
      });
    }
  });

  // Check health once when client becomes available
  $effect(() => {
    if (client && deploymentConfig && !hasCheckedHealth) {
      hasCheckedHealth = true;
      const healthcheckUrls = inferHealthEndpoint(deploymentConfig);
      if (healthcheckUrls.length > 0) {
        client.checkHealth(healthcheckUrls[0])
          .then(result => { isHealthy = result; })
          .catch(() => { isHealthy = false; });
      }
    }
  });

  // Check if auth is configured
  const isAuthConfigured = $derived(() => {
    const requiredSchemes = contract.security.requirements.flat();
    if (requiredSchemes.length === 0) return true;
    return requiredSchemes.some(scheme => authConfig[scheme]);
  });

  // Check if skill supports streaming
  const canStream = $derived(() => {
    if (!selectedSkill) return false;
    return selectedSkill.endpoints.some(e => e.streaming) && contract.capabilities.streaming;
  });

  const statusBadge = $derived(() => {
    if (isAuthConfigured() && isHealthy) {

      return {
        icon: CheckCircle,
        text: 'Ready',
        color: 'bg-secondary-300 text-secondary-950 border-secondary-950',
      };
    } else {
      return {
        icon: AlertCircle,
        text: 'Auth Required or Agent Unhealthy',
        color: 'bg-error-300 text-error-950 border-error-950',
      };
    }
  });

  // Helper functions for message handling
  function validateMessageInput(): boolean {
    return Boolean(message.trim() && selectedSkill && !isLoading && client);
  }

  function addUserMessage(content: string, debugPayload?: DebugPayload): void {
    messages = [...messages, {
      role: 'user',
      content,
      timestamp: new Date(),
      skillName: selectedSkill?.name,
      messageId: debugPayload?.messageId,
      debugPayload,
    }];
  }

  function addAgentMessage(content: string, debugPayload?: DebugPayload): void {
    messages = [...messages, {
      role: 'agent',
      content,
      timestamp: new Date(),
      skillName: selectedSkill?.name,
      messageId: debugPayload?.messageId,
      debugPayload,
    }];
  }

  function addSystemMessage(content: string): void {
    messages = [...messages, {
      role: 'system',
      content,
      timestamp: new Date(),
    }];
  }

  function updateLastMessage(content: string): void {
    messages = messages.map((msg, idx) =>
      idx === messages.length - 1 ? { ...msg, content } : msg
    );
  }

  async function handleStreamingResponse(userMessage: string): Promise<void> {
    if (!client || !selectedSkill) return;

    // Add empty agent message for streaming
    addAgentMessage('');

    const streamGenerator = client.invokeSkillStream({
      skill: selectedSkill,
      task: userMessage,
    });

    let accumulatedContent = '';
    for await (const chunk of streamGenerator) {
      accumulatedContent += chunk.data;
      streamingContent = accumulatedContent;
      updateLastMessage(accumulatedContent);

      if (chunk.done) break;
    }
  }

  function extractCleanResponse(response: unknown): string {
    // Type guard: ensure response is A2AResponse
    if (!isA2AResponse(response)) {
      return typeof response === 'string' ? response : JSON.stringify(response, null, 2);
    }

    // Handle failed responses
    if (response.status === 'failed') {
      return response.error?.message || 'Request failed';
    }

    const result = response.result;

    // Direct string response
    if (typeof result === 'string') {
      return result;
    }

    // Type-safe A2A Task extraction
    if (isA2ATask(result)) {
      const extracted = extractTextFromA2ATask(result);
      if (extracted) {
        return extracted;
      }
      // If no text found, show task status
      if (result.status) {
        return `Task ${result.status.state}: ${result.status.message || 'No message'}`;
      }
    }

    // Legacy format: result.parts[] array (non-A2A)
    if (typeof result === 'object' && result !== null && 'parts' in result && Array.isArray(result.parts)) {
      const textParts = result.parts
        .filter((part: any) => part.kind === 'text' && part.text)
        .map((part: any) => part.text);
      if (textParts.length > 0) {
        return textParts.join('\n\n');
      }
    }

    // Legacy format: result.message (non-A2A)
    if (typeof result === 'object' && result !== null && 'message' in result) {
      if (typeof result.message === 'string') {
        return result.message;
      }
      if (typeof result.message === 'object' && result.message !== null && 'parts' in result.message && Array.isArray(result.message.parts)) {
        const textParts = result.message.parts
          .filter((part: any) => part.kind === 'text' && part.text)
          .map((part: any) => part.text);
        if (textParts.length > 0) {
          return textParts.join('\n\n');
        }
      }
    }

    // Fallback
    return JSON.stringify(result, null, 2);
  }

  async function handleNonStreamingResponse(userMessage: string, messageId: string): Promise<void> {
    if (!client || !selectedSkill) return;

    const response = await client.invokeSkill({
      skill: selectedSkill,
      task: userMessage,
      messageId,
    });

    if (response.status === 'failed' && response.error) {
      const errorMsg = response.error.message;
      lastError = errorMsg;
      addSystemMessage(`❌ Error: ${errorMsg}`);
    } else {
      const cleanContent = extractCleanResponse(response);
      addAgentMessage(cleanContent, {
        messageId,
        response: JSON.parse(JSON.stringify(response)),
        timestamp: new Date(),
      });
    }
  }

  function handleMessageError(error: unknown): void {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    lastError = errorMessage;
    console.error('[AgentPlayground] Exception occurred:', error);
    addSystemMessage(`❌ Error: ${errorMessage}`);
  }

  async function sendMessage(): Promise<void> {
    if (!validateMessageInput()) return;

    const userMessage = message.trim();
    message = '';
    lastError = null;

    const messageId = crypto.randomUUID().replace(/-/g, '');

    addUserMessage(userMessage, {
      messageId,
      request: {
        skill: selectedSkill!.name,
        task: userMessage,
        timestamp: new Date().toISOString(),
      },
      timestamp: new Date(),
    });

    isLoading = true;
    streamingContent = '';

    try {
      if (useStreaming && canStream()) {
        await handleStreamingResponse(userMessage);
      } else {
        await handleNonStreamingResponse(userMessage, messageId);
      }
    } catch (error) {
      handleMessageError(error);
    } finally {
      isLoading = false;
      streamingContent = '';
    }
  }

  function handleKeyPress(e: KeyboardEvent): void {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  function useExample(example: string): void {
    message = example;
  }

  function openAuthConfig(): void {
    showAuthConfig = true;
  }

  function closeAuthConfig(): void {
    showAuthConfig = false;
  }

  function handleAuthSave(newConfig: Record<string, string>): void {
    authConfig = newConfig;
    closeAuthConfig();
  }
</script>

{#if showAuthConfig}
  <AgentAuthConfig
    securitySchemes={contract.security.schemes}
    {authConfig}
    onClose={closeAuthConfig}
    onSave={handleAuthSave}
  />
{/if}

<div class="flex flex-col flex-1 bg-surface-50 rounded-base">
  <!-- Header -->
  <div class="flex items-center justify-between gap-2 p-6 border-b-2 border-black bg-gradient-primary flex-shrink-0">
    <div class="flex items-center gap-3">
      <div class="p-2 bg-white rounded-lg border-2 border-black shadow-small">
        <Zap class="w-5 h-5 text-primary-800" />
      </div>
      <div>
        <h3 class="text-lg text-primary-950 font-bold">Agent Playground</h3>
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
        class="text-black px-3 py-1 text-xs bg-white rounded-lg border-2 border-black shadow-small shadow-hover transition-all font-bold"
      >
        Configure Auth
      </button>

      {#if messages.some(msg => msg.debugPayload)}
        <button
          onclick={openDebugSidebar}
          class="flex items-center gap-1 text-black px-3 py-1 text-xs bg-white rounded-lg border-2 border-black shadow-small hover:shadow-hover transition-all font-bold"
          title="View request/response history"
        >
          <Bug class="w-3 h-3" />
          Debug
        </button>
      {/if}

      {#if showCloseButton && onClose}
        <button
          onclick={onClose}
          class="p-2 bg-white text-primary-800 hover:bg-surface-100 rounded-lg transition-colors border-2 border-black shadow-small"
          aria-label="Close sidebar"
        >
          <X class="w-5 h-5" />
        </button>
      {/if}
    </div>
  </div>

  <!-- Skill Selection -->
  {#if contract.skills.length > 1}
    <div class="p-3 border-b-2 border-black bg-surface-500">
      <label for="skill-select" class="text-xs font-bold text-gray-700 mb-1 block">Select Skill:</label>
      <div class="flex flex-wrap gap-2">
        {#each contract.skills as skill}
          <button
            onclick={() => selectedSkill = skill}
            class="px-3 py-1 text-xs rounded-lg border-2 border-black shadow-small shadow-hover transition-all {selectedSkill?.skillId === skill.skillId ? 'bg-primary-500 text-white font-bold' : 'bg-white text-gray-900 hover:bg-gray-100'}"
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
      {#each messages as msg, idx}
        <div class="flex {msg.role === 'user' ? 'justify-end' : 'justify-start'} {idx === selectedDebugIndex && showDebugSidebar ? 'relative' : ''}">
          <div class="max-w-[80%] {idx === selectedDebugIndex && showDebugSidebar ? 'ring-2 ring-primary-500 rounded-lg' : ''}">
            <div class="text-xs text-gray-500 mb-1 {msg.role === 'user' ? 'text-right' : 'text-left'}">
              {msg.role === 'user' ? 'You' : msg.role === 'system' ? 'System' : agentName}
              {#if msg.skillName}
                • <span class="italic">{msg.skillName}</span>
              {/if}
              • {msg.timestamp.toLocaleTimeString()}
              {#if msg.debugPayload}
                <button
                  onclick={() => { selectedDebugIndex = idx; openDebugSidebar(); }}
                  class="ml-1 inline-flex items-center gap-0.5 text-primary-600 hover:text-primary-800 font-bold"
                  title={msg.role === 'user' ? 'View request' : 'View response'}
                >
                  <Bug class="w-3 h-3" />
                </button>
              {/if}
            </div>
            <div class="p-3 rounded-lg border-2 border-black shadow-small {msg.role === 'user' ? 'bg-primary-100' : msg.role === 'system' || msg.role === 'agent' ? 'bg-surface-100' : 'bg-white'} whitespace-pre-wrap">
              <p class="text-sm {msg.role === 'user' ? 'text-primary-950' : msg.role === 'system' || msg.role === 'agent' ? 'text-black' : 'text-white'}">{msg.content}</p>
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
  <div class="p-4 border-t-2 border-black bg-surface-100 rounded-b-base">
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
        disabled={!validateMessageInput()}
        class="px-4 py-2 bg-primary-500 text-white font-bold rounded-lg border-2 border-black shadow shadow-hover disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
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

{#if showDebugSidebar && debugMessages.length > 0}
  <DebugPayloadSidebar
    {debugMessages}
    selectedIndex={selectedDebugIndex ?? debugMessages[debugMessages.length - 1].index}
    onSelectIndex={(idx) => { selectedDebugIndex = idx; }}
    onClose={closeDebugSidebar}
  />
{/if}
