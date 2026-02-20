<script lang="ts">
  import { Info, Send, MessageCircle, Clock, CheckCircle, AlertCircle } from 'lucide-svelte';
  import Pill from '$lib/components/utils/Pill.svelte';
  import CodeBlock from '$lib/components/codeblock/CodeBlock.svelte';
  import type { A2AResponse, A2ATask, DebugPayload } from './types';
  import { isA2AResponse, isA2ATask } from './types';

 

  let {
    payload,
    role,
    skillName,
  }: {
    payload: DebugPayload;
    role: 'user' | 'agent' | 'system';
    skillName?: string;
  } = $props();

  const requestJson = $derived(payload.request ? JSON.stringify(payload.request, null, 2) : null);
  const responseJson = $derived(payload.response ? JSON.stringify(payload.response, null, 2) : null);

  // Extract A2A task info if available
  const a2aInfo = $derived.by(() => {
    if (!isA2AResponse(payload.response)) return null;
    
    const response = payload.response as A2AResponse;
    if (!isA2ATask(response.result)) return null;
    
    const task = response.result as A2ATask;
    return {
      taskId: task.id,
      contextId: task.contextId,
      status: task.status,
      artifactCount: task.artifacts?.length || 0,
      historyCount: task.history?.length || 0,
    };
  });
</script>

<div class="flex flex-col h-full bg-white">
  <!-- Header -->
  <div class="p-3 border-b-2 border-black bg-surface-50">
    <div class="flex items-start gap-2">
      <div class="w-1 h-14 rounded {role === 'user' ? 'bg-primary-500' : 'bg-secondary-500'}"></div>
      <div class="flex-1 min-w-0">
        <h3 class="font-bold text-gray-900">{role === 'user' ? 'Request' : 'Response'}</h3>
        <p class="text-sm text-gray-600 flex items-center gap-1.5 flex-wrap">
          <span class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-bold border {role === 'user' ? 'bg-primary-100 text-primary-900 border-primary-800' : 'bg-secondary-100 text-secondary-900 border-secondary-800'}">
            {role === 'user' ? 'USER' : 'AGENT'}
          </span>
          {#if payload.messageId}
            <span class="font-mono text-xs text-gray-500 bg-surface-200 px-1.5 py-0.5 rounded border border-gray-300">{payload.messageId}</span>
          {/if}
        </p>
        {#if skillName}
          <p class="text-xs font-mono text-gray-500 mt-1">{skillName}</p>
        {/if}
      </div>
    </div>
  </div>

  <!-- Scrollable Content -->
  <div class="flex-1 overflow-auto p-4 space-y-4">

    <!-- Timing Information -->
    <section>
      <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
        <Clock color="#8059b6"/>
        <header class="pl-2 text-primary-950 text-sm font-bold">Timing</header>
      </div>

      <div class="flex flex-col space-y-1 text-sm">
        <Pill key="Timestamp" value={payload.timestamp.toLocaleString()} textSize="text-xs"/>
      </div>
    </section>

    <!-- A2A Task Summary (if available) -->
    {#if a2aInfo}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
          <Info color="#8059b6"/>
          <header class="pl-2 text-primary-950 text-sm font-bold">A2A Task Summary</header>
        </div>

        <div class="flex flex-col space-y-1 text-sm">
          <Pill key="Task ID" value={a2aInfo.taskId} textSize="text-xs"/>
          {#if a2aInfo.contextId}
            <Pill key="Context ID" value={a2aInfo.contextId} textSize="text-xs"/>
          {/if}
          {#if a2aInfo.status}
            <Pill 
              key="Status" 
              value={a2aInfo.status.state} 
              textSize="text-xs"
              bgColor={a2aInfo.status.state === 'completed' ? 'bg-secondary-100' : a2aInfo.status.state === 'failed' ? 'bg-error-100' : 'bg-warning-100'}
              textColor={a2aInfo.status.state === 'completed' ? 'text-secondary-950' : a2aInfo.status.state === 'failed' ? 'text-error-950' : 'text-warning-950'}
              borderColor={a2aInfo.status.state === 'completed' ? 'border-secondary-950' : a2aInfo.status.state === 'failed' ? 'border-error-950' : 'border-warning-950'}
            />
          {/if}
          <Pill key="Artifacts" value={`${a2aInfo.artifactCount} artifact${a2aInfo.artifactCount !== 1 ? 's' : ''}`} textSize="text-xs"/>
          <Pill key="Task Turns" value={`${a2aInfo.historyCount} turn${a2aInfo.historyCount !== 1 ? 's' : ''}`} textSize="text-xs"/>
        </div>
      </section>
    {/if}

    <!-- Request Details -->
    {#if requestJson}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
          <Send color="#8059b6"/>
          <header class="pl-2 text-primary-950 text-sm font-bold">Request</header>
        </div>

        <div class="rounded-lg border-2 border-black bg-surface-50 overflow-y-scroll max-h-[600px] text-xs">
          <CodeBlock code={requestJson} lang="json" />
        </div>
      </section>
    {/if}

    <!-- Response Details -->
    {#if responseJson}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
          <MessageCircle color="#8059b6"/>
          <header class="pl-2 text-primary-950 text-sm font-bold">Response</header>
        </div>

        <div class="rounded-lg border-2 border-black bg-surface-50 overflow-y-scroll max-h-[600px] text-xs">
          <CodeBlock code={responseJson} lang="json" />
        </div>
      </section>
    {/if}

  </div>
</div>
