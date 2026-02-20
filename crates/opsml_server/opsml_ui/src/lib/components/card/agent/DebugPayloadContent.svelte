<script lang="ts">
  import { Info, Send, MessageCircle, Clock } from 'lucide-svelte';
  import Pill from '$lib/components/utils/Pill.svelte';
  import CodeBlock from '$lib/components/codeblock/CodeBlock.svelte';
  import { isTask, type DebugPayload, type SendMessageResponse } from './types';
  import { isAdkMetadata, type AdkMetadata } from './agentClient';

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
  const messageResponse = $derived.by(() => {
    if (payload.response && typeof payload.response === 'object') {
      console.log('DebugPayload response:', responseJson);
      return (payload.response as SendMessageResponse);
    }
    return null;
  });

  const taskMetadata = $derived.by(() => {
    if (messageResponse && isTask(messageResponse) && messageResponse.metadata) {
      return messageResponse.metadata;
    }
    return null;
  });

  const adkMetadata = $derived.by(() => {
    if (taskMetadata && isAdkMetadata(taskMetadata)) {
      return taskMetadata as AdkMetadata;
    }
    return null;
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
    {#if messageResponse && isTask(messageResponse)}
    {@const task = messageResponse}
      <section>
        <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
          <Info color="#8059b6"/>
          <header class="pl-2 text-primary-950 text-sm font-bold">A2A Task Summary</header>
        </div>

        <div class="flex flex-col space-y-1 text-sm">
          <Pill key="Task ID" value={task.id} textSize="text-xs"/>
          {#if task.contextId}
            <Pill key="Context ID" value={task.contextId} textSize="text-xs"/>
          {/if}
          {#if task.status}
            <Pill
              key="Status"
              value={task.status.state}
              textSize="text-xs"
              bgColor={task.status.state === 'TASK_STATE_COMPLETED' ? 'bg-secondary-100' : task.status.state === 'TASK_STATE_FAILED' ? 'bg-error-100' : 'bg-warning-100'}
              textColor={task.status.state === 'TASK_STATE_COMPLETED' ? 'text-secondary-950' : task.status.state === 'TASK_STATE_FAILED' ? 'text-error-950' : 'text-warning-950'}
              borderColor={task.status.state === 'TASK_STATE_COMPLETED' ? 'border-secondary-950' : task.status.state === 'TASK_STATE_FAILED' ? 'border-error-950' : 'border-warning-950'}
            />
          {/if}
          {#if task.artifacts}
            <Pill key="Artifacts" value={`${task.artifacts.length} artifact${task.artifacts.length !== 1 ? 's' : ''}`} textSize="text-xs"/>
          {/if}
          {#if task.history}
            <Pill key="Task Turns" value={`${task.history.length} turn${task.history.length !== 1 ? 's' : ''}`} textSize="text-xs"/>
          {/if}
        </div>
      </section>

      <!-- ADK Metadata -->
      {#if adkMetadata}
        <section>
          <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
            <Info color="#8059b6"/>
            <header class="pl-2 text-primary-950 text-sm font-bold">ADK Metadata</header>
          </div>
          <div class="flex flex-col space-y-1 text-sm">
            {#if adkMetadata.adk_app_name}
              <Pill key="App" value={adkMetadata.adk_app_name} textSize="text-xs"/>
            {/if}
            {#if adkMetadata.adk_author}
              <Pill key="Author" value={adkMetadata.adk_author} textSize="text-xs"/>
            {/if}
            {#if adkMetadata.adk_user_id}
              <Pill key="User" value={adkMetadata.adk_user_id} textSize="text-xs"/>
            {/if}
            {#if adkMetadata.adk_session_id}
              <Pill key="Session" value={adkMetadata.adk_session_id} textSize="text-xs"/>
            {/if}
            {#if adkMetadata.adk_invocation_id}
              <Pill key="Invocation" value={adkMetadata.adk_invocation_id} textSize="text-xs"/>
            {/if}
            {#if adkMetadata.adk_event_id}
              <Pill key="Event" value={adkMetadata.adk_event_id} textSize="text-xs"/>
            {/if}
          </div>
          {#if adkMetadata.adk_usage_metadata}
            {@const usage = adkMetadata.adk_usage_metadata}
            <div class="mt-3">
              <p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Token Usage</p>
              <div class="flex flex-wrap gap-2">
                <Pill key="Total" value={String(usage.totalTokenCount)} textSize="text-xs"/>
                <Pill key="Prompt" value={String(usage.promptTokenCount)} textSize="text-xs"/>
                <Pill key="Candidates" value={String(usage.candidatesTokenCount)} textSize="text-xs"/>
                {#if usage.thoughtsTokenCount}
                  <Pill key="Thoughts" value={String(usage.thoughtsTokenCount)} textSize="text-xs"/>
                {/if}
              </div>
            </div>
          {/if}
        </section>

      <!-- Generic Metadata -->
      {:else if taskMetadata}
        <section>
          <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
            <Info color="#8059b6"/>
            <header class="pl-2 text-primary-950 text-sm font-bold">Metadata</header>
          </div>
          <div class="flex flex-col space-y-1 text-sm">
            {#each Object.entries(taskMetadata) as [key, value]}
              <Pill {key} value={typeof value === 'string' ? value : JSON.stringify(value)} textSize="text-xs"/>
            {/each}
          </div>
        </section>
      {/if}
    {/if}

    <!-- Request Details -->
    {#if requestJson && role === 'user'}
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
    {#if responseJson && role === 'agent'}
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
