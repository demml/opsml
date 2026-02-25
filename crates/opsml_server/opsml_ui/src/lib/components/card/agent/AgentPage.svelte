<script lang="ts">
  import type { ServiceCard } from '$lib/components/card/card_interfaces/servicecard';
  import type { AgentSpec } from './types';
  import AgentMetadata from './AgentMetadata.svelte';
  import AgentCapabilities from './AgentCapabilities.svelte';
  import AgentSkills from './AgentSkills.svelte';
  import AgentInterfaces from './AgentInterfaces.svelte';
  import AgentCards from './AgentCards.svelte';
  import { Activity, ExternalLink, Bot } from 'lucide-svelte';

  let { data } = $props();
  let service: ServiceCard = data.metadata;
  let agentSpec: AgentSpec | undefined = service.service_config.agent;
</script>

{#if !agentSpec}
  <div class="flex-1 mx-auto w-11/12 pt-6 px-4 pb-10">
    <div class="rounded-base border-2 border-black shadow bg-error-100 p-8 text-center">
      <p class="text-lg font-bold text-error-900">No agent specification found for this service.</p>
    </div>
  </div>
{:else}
  <div class="flex-1 mx-auto w-11/12 pt-6 px-4 pb-10">

    <div class="mb-8 border-2 border-black shadow bg-primary-100 p-5 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-4">
        <div class="p-3 bg-primary-500 border-2 border-black shadow-small rounded-base">
          <Bot class="w-7 h-7 text-white" />
        </div>
        <div>
          <div class="flex items-center gap-3 mb-1">
            <h1 class="text-2xl font-black text-black">{agentSpec.name}</h1>
            <span class="badge bg-primary-500 text-white border-2 border-black shadow-small text-xs font-black uppercase tracking-wider px-2 py-0.5">
              A2A
            </span>
            <span class="badge bg-surface-50 text-primary-800 border-2 border-black shadow-small text-xs font-bold px-2 py-0.5">
              v{agentSpec.version}
            </span>
          </div>
          <p class="text-sm font-mono text-primary-700 font-bold">Agent Card • A2A Specification</p>
        </div>
      </div>

      <div class="flex flex-wrap gap-2">
        {#if agentSpec.documentationUrl}
          <a
            href={agentSpec.documentationUrl}
            target="_blank"
            rel="noopener noreferrer"
            class="btn bg-surface-50 text-primary-800 border-2 border-black shadow-small shadow-hover-small rounded-base px-4 py-2 gap-2 flex items-center font-bold transition-all duration-100"
          >
            <ExternalLink class="w-4 h-4" />
            Docs
          </a>
        {/if}
      </div>
    </div>

    <!-- ── Main Content Grid ── -->
    <div class="flex flex-wrap gap-6 w-full">

      <!-- Left Column: Metadata & Capabilities -->
      <div class="flex-1 min-w-[26rem] max-w-[32rem] space-y-5">

        <!-- Agent Metadata -->
        <div class="rounded-base bg-surface-50 border-2 border-black shadow-primary p-4 max-h-[600px] overflow-y-auto">
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

      <!-- Right Column: Skills, Cards, Security -->
      <div class="flex-1 space-y-5">

        <!-- Skills -->
        {#if agentSpec.skills.length > 0}
          <AgentSkills skills={agentSpec.skills} />
        {/if}

        <!-- Associated Cards -->
        {#if service.cards && service.cards.cards.length > 0}
          <AgentCards cards={service.cards.cards} />
        {/if}

        <!-- Security Requirements -->
        {#if agentSpec.securityRequirements && agentSpec.securityRequirements.length > 0}
          <div class="rounded-base border-2 border-black shadow warn-color p-4">
            <div class="flex items-center gap-2 mb-3 pb-2 border-b-2 border-black">
              <Activity class="w-5 h-5 text-black flex-shrink-0" />
              <h4 class="text-sm font-black text-black uppercase tracking-wide">Security Requirements</h4>
            </div>
            <div class="space-y-2">
              {#each agentSpec.securityRequirements as requirement}
                <div class="flex items-center gap-2 p-2 bg-warning-300 rounded-base border border-black">
                  <span class="text-xs text-black/80">Required schemes:</span>
                  <span class="text-xs font-black text-black">{requirement.schemes.join(', ')}</span>
                </div>
              {/each}
            </div>
          </div>
        {/if}

        <!-- Security Schemes -->
        {#if agentSpec.securitySchemes}
          <div class="rounded-base border-2 border-black shadow bg-surface-50 p-4">
            <div class="flex items-center gap-2 mb-3 pb-3 border-b-2 border-black">
              <div class="p-1.5 bg-warning-300 border-2 border-black rounded-base">
                <Activity class="w-4 h-4 text-black" />
              </div>
              <h3 class="text-base font-black text-primary-950 uppercase tracking-wide">Security Schemes</h3>
            </div>
            <div class="space-y-2">
              {#each Object.entries(agentSpec.securitySchemes) as [schemeName, scheme]}
                <details class="rounded-base border-2 border-black bg-surface-50 overflow-hidden">
                  <summary class="px-3 py-2 text-sm font-bold text-primary-950 cursor-pointer hover:bg-primary-50 transition-colors duration-100">
                    {schemeName}
                  </summary>
                  <pre class="m-3 p-3 bg-surface-100 rounded-base border border-black text-xs overflow-x-auto font-mono leading-relaxed">{JSON.stringify(scheme, null, 2)}</pre>
                </details>
              {/each}
            </div>
          </div>
        {/if}

        <!-- Digital Signatures -->
        {#if agentSpec.signatures && agentSpec.signatures.length > 0}
          <div class="rounded-base border-2 border-black shadow bg-surface-50 p-4">
            <div class="flex items-center gap-2 mb-3 pb-3 border-b-2 border-black">
              <h3 class="text-base font-black text-primary-950 uppercase tracking-wide">Digital Signatures</h3>
              <span class="badge bg-primary-100 text-primary-800 border border-black text-xs font-bold">{agentSpec.signatures.length}</span>
            </div>
            <div class="space-y-2">
              {#each agentSpec.signatures as signature, idx}
                <details class="rounded-base border-2 border-black overflow-hidden">
                  <summary class="px-3 py-2 text-sm font-bold text-primary-950 cursor-pointer hover:bg-primary-50 transition-colors duration-100">
                    Signature {idx + 1}
                  </summary>
                  <div class="p-3 space-y-3 border-t-2 border-black">
                    <div>
                      <span class="text-xs font-black text-primary-700 uppercase tracking-wide">Protected</span>
                      <pre class="mt-1 p-2 bg-surface-100 rounded-base border border-black text-xs overflow-x-auto font-mono">{signature.protected}</pre>
                    </div>
                    <div>
                      <span class="text-xs font-black text-primary-700 uppercase tracking-wide">Signature</span>
                      <pre class="mt-1 p-2 bg-surface-100 rounded-base border border-black text-xs overflow-x-auto font-mono">{signature.signature}</pre>
                    </div>
                    {#if signature.header}
                      <div>
                        <span class="text-xs font-black text-primary-700 uppercase tracking-wide">Header</span>
                        <pre class="mt-1 p-2 bg-surface-100 rounded-base border border-black text-xs overflow-x-auto font-mono">{JSON.stringify(signature.header, null, 2)}</pre>
                      </div>
                    {/if}
                  </div>
                </details>
              {/each}
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}