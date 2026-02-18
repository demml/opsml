<script lang="ts">
  import type { ServiceCard } from '$lib/components/card/card_interfaces/servicecard';
  import type { AgentSpec } from './types';
  import AgentMetadata from './AgentMetadata.svelte';
  import AgentCapabilities from './AgentCapabilities.svelte';
  import AgentSkills from './AgentSkills.svelte';
  import AgentInterfaces from './AgentInterfaces.svelte';
  import AgentCards from './AgentCards.svelte';
  import EnhancedAgentPlayground from './EnhancedAgentPlayground.svelte';
  import { Activity, ExternalLink } from 'lucide-svelte';

  let { data } = $props();
  let service: ServiceCard = data.metadata;
  let agentSpec: AgentSpec | undefined = service.service_config.agent;

</script>

{#if !agentSpec}
  <div class="flex-1 mx-auto w-11/12 pt-6 px-4 pb-10">
    <div class="rounded-lg border-2 border-black shadow-small bg-error-100 p-8 text-center">
      <p class="text-lg font-bold text-error-900">No agent specification found for this service.</p>
    </div>
  </div>
{:else}
  <div class="flex-1 mx-auto w-11/12 pt-6 px-4 pb-10">

    <!-- Header Section with Quick Actions -->
    <div class="mb-6 flex flex-wrap items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-primary-800 mb-2">{agentSpec.name}</h1>
        <p class="text-sm text-gray-600">Agent Card • A2A Specification v{agentSpec.version}</p>
      </div>

      <div class="flex flex-wrap gap-2">

        {#if agentSpec.documentationUrl}
          <a
            href={agentSpec.documentationUrl}
            target="_blank"
            rel="noopener noreferrer"
            class="btn bg-surface-100 text-gray-700 hover:bg-surface-200 border-gray-300 border-2 px-4 py-2 gap-2 flex items-center"
          >
            <ExternalLink class="w-4 h-4" />
            Docs
          </a>
        {/if}
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="flex flex-wrap gap-4 w-full">

      <!-- Left Column: Metadata & Capabilities -->
      <div class="flex-1 min-w-[26rem] max-w-[32rem] space-y-4">
        <!-- Agent Metadata -->
        <div class="rounded-base bg-surface-50 border-primary-800 border-3 shadow-primary p-4 max-h-[600px] overflow-y-auto">
          <AgentMetadata
            {agentSpec}
            uid={service.uid}
            createdAt={service.created_at}
            space={service.space}
            name={service.name}
            version={service.version}
          />
        </div>

        <!-- Capabilities -->
        <AgentCapabilities capabilities={agentSpec.capabilities} />

        <!-- Supported Interfaces -->
        {#if agentSpec.supportedInterfaces.length > 0}
          <AgentInterfaces interfaces={agentSpec.supportedInterfaces} />
        {/if}
      </div>

      <!-- Middle Column: Skills, Details & Cards -->
      <div class="flex-1 space-y-4">
        <!-- Skills -->
        {#if agentSpec.skills.length > 0}
          <AgentSkills skills={agentSpec.skills} />
        {/if}

        <!-- Associated Cards -->
        {#if service.cards && service.cards.cards.length > 0}
          <AgentCards cards={service.cards.cards} />
        {/if}

        <!-- Security Notice -->
        {#if agentSpec.securityRequirements && agentSpec.securityRequirements.length > 0}
          <div class="rounded-lg border-2 border-black shadow-small bg-warning-100 p-4">
            <div class="flex items-start gap-2">
              <Activity class="w-5 h-5 text-warning-800 flex-shrink-0" />
              <div>
                <h4 class="text-sm font-bold text-warning-900 mb-2">Security Requirements</h4>
                <div class="space-y-2">
                  {#each agentSpec.securityRequirements as requirement}
                    <div class="text-xs text-warning-800">
                      Required schemes: <span class="font-bold">{requirement.schemes.join(', ')}</span>
                    </div>
                  {/each}
                </div>
              </div>
            </div>
          </div>
        {/if}

        <!-- Security Schemes -->
        {#if agentSpec.securitySchemes}
          <div class="rounded-lg border-2 border-black shadow-small bg-surface-50 p-4">
            <div class="flex items-center gap-2 mb-3 pb-3 border-b-2 border-black">
              <Activity class="w-5 h-5 text-primary-800" />
              <h3 class="text-lg font-bold text-primary-950">Security Schemes</h3>
            </div>
            <div class="space-y-2">
              {#each Object.entries(agentSpec.securitySchemes) as [name, scheme]}
                <details class="p-2 bg-white rounded border-2 border-black">
                  <summary class="text-sm font-bold text-gray-900 cursor-pointer hover:text-primary-800">
                    {name}
                  </summary>
                  <pre class="mt-2 p-2 bg-surface-100 rounded text-xs overflow-x-auto">{JSON.stringify(scheme, null, 2)}</pre>
                </details>
              {/each}
            </div>
          </div>
        {/if}
      </div>
    </div>

    <!-- Optional: Signatures Section -->
    {#if agentSpec.signatures && agentSpec.signatures.length > 0}
      <div class="mt-6 rounded-lg border-2 border-black shadow-small bg-surface-50 p-4">
        <h3 class="text-lg font-bold text-primary-950 mb-3">Digital Signatures</h3>
        <div class="space-y-2">
          {#each agentSpec.signatures as signature}
            <details class="p-3 bg-white rounded border-2 border-black">
              <summary class="text-sm font-bold text-gray-900 cursor-pointer hover:text-primary-800">
                View Signature
              </summary>
              <div class="mt-2 space-y-2">
                <div>
                  <span class="text-xs font-bold text-gray-600">Protected:</span>
                  <pre class="mt-1 p-2 bg-surface-100 rounded text-xs overflow-x-auto">{signature.protected}</pre>
                </div>
                <div>
                  <span class="text-xs font-bold text-gray-600">Signature:</span>
                  <pre class="mt-1 p-2 bg-surface-100 rounded text-xs overflow-x-auto">{signature.signature}</pre>
                </div>
                {#if signature.header}
                  <div>
                    <span class="text-xs font-bold text-gray-600">Header:</span>
                    <pre class="mt-1 p-2 bg-surface-100 rounded text-xs overflow-x-auto">{JSON.stringify(signature.header, null, 2)}</pre>
                  </div>
                {/if}
              </div>
            </details>
          {/each}
        </div>
      </div>
    {/if}
  </div>
{/if}