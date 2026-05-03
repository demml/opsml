<script lang="ts">
  import type { GenAiSpanRecord } from "$lib/components/scouter/genai/types";
  import { parseMessages, safeParseJson, prettyJson } from "./messageFormat";
  import { fmtInt } from "$lib/components/card/agent/observability/format";
  import {
    BadgeCheck,
    Database,
    MessageSquare,
    Server,
    Settings2,
  } from "lucide-svelte";
  import MessageList from "./MessageList.svelte";
  import EvalResultRow from "./EvalResultRow.svelte";
  import ToolCallBlock from "./ToolCallBlock.svelte";

  let { span }: { span: GenAiSpanRecord } = $props();

  type SpanGenAiTab =
    | "messages"
    | "eval"
    | "params"
    | "agent"
    | "tool"
    | "server"
    | "raw";

  let genAiTab = $state<SpanGenAiTab>("messages");

  const genAiSubTabs: { key: SpanGenAiTab; label: string }[] = [
    { key: "messages", label: "Messages" },
    { key: "eval", label: "Eval" },
    { key: "params", label: "Request" },
    { key: "agent", label: "Agent" },
    { key: "tool", label: "Tool" },
    { key: "server", label: "Server" },
    { key: "raw", label: "Raw" },
  ];

  const inputMessages = $derived(parseMessages(span.input_messages));
  const outputMessages = $derived(parseMessages(span.output_messages));
  const toolDefinitionsParsed = $derived(safeParseJson(span.tool_definitions));
</script>

<div class="flex flex-col">
  <div
    class="sticky top-0 z-10 flex border-b-2 border-black bg-surface-100 overflow-x-auto"
  >
    {#each genAiSubTabs as t (t.key)}
      <button
        onclick={() => (genAiTab = t.key)}
        class="px-3 py-1.5 text-xs font-black uppercase tracking-wide border-r-2 border-black transition-colors duration-100
          {genAiTab === t.key
          ? 'bg-primary-200 text-primary-900'
          : 'text-primary-600 hover:text-primary-800 hover:bg-surface-200'}"
      >
        {t.label}
      </button>
    {/each}
  </div>

  <div class="p-3">
    {#if genAiTab === "messages"}
      <div class="space-y-4">
        {#if span.system_instructions}
          <div>
            <div
              class="text-xs font-black uppercase text-primary-700 mb-1.5"
            >
              system_instructions
            </div>
            <div class="border border-black rounded-base overflow-hidden">
              <div
                class="flex items-center gap-1.5 px-2 py-1 border-b border-black bg-surface-200"
              >
                <span
                  class="text-xs font-black uppercase tracking-widest text-primary-600"
                  >system</span
                >
              </div>
              <div class="px-2.5 py-2 bg-surface-50">
                <p
                  class="text-xs font-mono whitespace-pre-wrap text-primary-900 leading-relaxed"
                >
                  {span.system_instructions}
                </p>
              </div>
            </div>
          </div>
        {/if}

        {#if span.input_messages}
          <div>
            <div
              class="text-xs font-black uppercase text-primary-700 mb-1.5 flex items-center gap-1"
            >
              <MessageSquare class="w-3 h-3" /> input_messages
              {#if span.input_tokens != null}
                <span class="font-mono text-primary-600 ml-1"
                  >{fmtInt(span.input_tokens)} tok</span
                >
              {/if}
            </div>
            {#if inputMessages}
              <MessageList messages={inputMessages} />
            {:else}
              <pre
                class="text-xs bg-surface-100 border border-black rounded-base p-2 overflow-x-auto font-mono text-primary-900">{prettyJson(
                  span.input_messages,
                )}</pre>
            {/if}
          </div>
        {/if}

        {#if span.output_messages}
          <div>
            <div
              class="text-xs font-black uppercase text-primary-700 mb-1.5 flex items-center gap-1"
            >
              <MessageSquare class="w-3 h-3" /> output_messages
              {#if span.output_tokens != null}
                <span class="font-mono text-primary-600 ml-1"
                  >{fmtInt(span.output_tokens)} tok</span
                >
              {/if}
            </div>
            {#if outputMessages}
              <MessageList messages={outputMessages} />
            {:else}
              <pre
                class="text-xs bg-surface-100 border border-black rounded-base p-2 overflow-x-auto font-mono text-primary-900">{prettyJson(
                  span.output_messages,
                )}</pre>
            {/if}
          </div>
        {/if}

        {#if span.tool_definitions}
          <div>
            <div
              class="text-xs font-black uppercase text-primary-700 mb-1.5 flex items-center gap-1"
            >
              <Database class="w-3 h-3" /> tool_definitions
            </div>
            <ToolCallBlock {span} toolDefinitions={toolDefinitionsParsed} />
          </div>
        {/if}

        {#if !span.system_instructions && !span.input_messages && !span.output_messages}
          <div class="text-center text-primary-600 italic text-xs py-6">
            no message content captured for this span
          </div>
        {/if}
      </div>
    {:else if genAiTab === "eval"}
      {#if span.eval_results.length === 0}
        <div
          class="text-center text-primary-600 italic text-xs py-6 flex flex-col items-center gap-2"
        >
          <BadgeCheck class="w-8 h-8 opacity-30" />
          no eval_results recorded for this span
        </div>
      {:else}
        <div class="space-y-2">
          {#each span.eval_results as e, i (i)}
            <EvalResultRow ev={e} />
          {/each}
        </div>
      {/if}
    {:else if genAiTab === "params"}
      <div class="space-y-2">
        <div class="grid grid-cols-2 md:grid-cols-3 gap-1.5">
          {#each [
            { k: "request_model", v: span.request_model },
            { k: "response_model", v: span.response_model },
            { k: "response_id", v: span.response_id },
            { k: "temperature", v: span.request_temperature },
            { k: "max_tokens", v: span.request_max_tokens },
            { k: "top_p", v: span.request_top_p },
            { k: "seed", v: span.request_seed },
            { k: "freq_penalty", v: span.request_frequency_penalty },
            { k: "presence_penalty", v: span.request_presence_penalty },
            { k: "choice_count", v: span.request_choice_count },
            { k: "finish_reasons", v: span.finish_reasons.join(", ") || null },
            { k: "output_type", v: span.output_type },
            { k: "input_tokens", v: span.input_tokens },
            { k: "output_tokens", v: span.output_tokens },
            { k: "cache_creation_tok", v: span.cache_creation_input_tokens },
            { k: "cache_read_tok", v: span.cache_read_input_tokens },
          ] as row (row.k)}
            <div
              class="border border-black rounded-base bg-surface-100 px-2 py-1"
            >
              <div
                class="text-xs font-black text-primary-700 uppercase tracking-widest flex items-center gap-1"
              >
                <Settings2 class="w-2.5 h-2.5" />
                {row.k}
              </div>
              <div class="text-xs font-mono text-primary-900 leading-tight">
                {row.v ?? "—"}
              </div>
            </div>
          {/each}
        </div>
        {#if span.request_stop_sequences.length > 0}
          <div
            class="border border-black rounded-base bg-surface-100 px-2 py-1"
          >
            <div class="text-xs font-black text-primary-700 uppercase">
              stop_sequences
            </div>
            <div class="text-xs font-mono text-primary-900">
              {span.request_stop_sequences.join(" · ")}
            </div>
          </div>
        {/if}
      </div>
    {:else if genAiTab === "agent"}
      <div class="grid grid-cols-1 md:grid-cols-2 gap-1.5">
        {#each [
          { k: "agent_name", v: span.agent_name },
          { k: "agent_id", v: span.agent_id },
          { k: "agent_version", v: span.agent_version },
          { k: "agent_description", v: span.agent_description },
          { k: "conversation_id", v: span.conversation_id },
          { k: "data_source_id", v: span.data_source_id },
          { k: "label", v: span.label },
          { k: "operation_name", v: span.operation_name },
          { k: "provider_name", v: span.provider_name },
        ] as row (row.k)}
          <div
            class="border border-black rounded-base bg-surface-100 px-2 py-1"
          >
            <div
              class="text-xs font-black text-primary-700 uppercase tracking-widest"
            >
              {row.k}
            </div>
            <div
              class="text-xs font-mono text-primary-900 break-all leading-tight"
            >
              {row.v ?? "—"}
            </div>
          </div>
        {/each}
      </div>
    {:else if genAiTab === "tool"}
      {#if !span.tool_name && !span.tool_call_id}
        <div class="text-center text-primary-600 italic text-xs py-4">
          no tool data for this span
        </div>
      {:else}
        <ToolCallBlock {span} />
      {/if}
    {:else if genAiTab === "server"}
      <div class="grid grid-cols-2 md:grid-cols-3 gap-1.5">
        {#each [
          { k: "server_address", v: span.server_address },
          { k: "server_port", v: span.server_port },
          { k: "openai_api_type", v: span.openai_api_type },
          { k: "openai_service_tier", v: span.openai_service_tier },
        ] as row (row.k)}
          <div
            class="border border-black rounded-base bg-surface-100 px-2 py-1"
          >
            <div
              class="text-xs font-black text-primary-700 uppercase flex items-center gap-1"
            >
              <Server class="w-2.5 h-2.5" />
              {row.k}
            </div>
            <div class="text-xs font-mono break-all text-primary-900">
              {row.v ?? "—"}
            </div>
          </div>
        {/each}
      </div>
    {:else if genAiTab === "raw"}
      <pre
        class="text-xs font-mono bg-surface-100 border border-black rounded-base p-2 overflow-x-auto text-primary-900">{JSON.stringify(
          span,
          null,
          2,
        )}</pre>
    {/if}
  </div>
</div>
