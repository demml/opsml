<script lang="ts">
  import { Filter } from 'lucide-svelte';
  import CustomSelect from '$lib/components/utils/CustomSelect.svelte';
  import type { AppliedFilters, AvailableFilters, EvalProfileOption } from './types';

  let {
    available,
    applied,
    evalProfiles = [],
    lockEntity = false,
    onChange,
  }: {
    available: AvailableFilters;
    applied: AppliedFilters;
    evalProfiles?: EvalProfileOption[];
    /**
     * When true the Profile select is rendered but disabled and pinned to the
     * current `applied.entity_id`. Used by the PromptCard scope where the
     * entity is implicit and must not be cleared.
     */
    lockEntity?: boolean;
    onChange: (next: {
      agent_name: string | null;
      model: string | null;
      provider_name: string | null;
      operation_name: string | null;
      entity_id: string | null;
    }) => void;
  } = $props();

  const agentOptions = $derived(
    Array.from(
      new Set(
        available.agents
          .map((a) => a.agent_name)
          .filter((n): n is string => !!n),
      ),
    )
      .sort()
      .map((n) => ({ value: n, label: n })),
  );

  const modelOptions = $derived(available.models.map((m) => ({ value: m, label: m })));
  const providerOptions = $derived(available.providers.map((p) => ({ value: p, label: p })));
  const operationOptions = $derived(available.operations.map((op) => ({ value: op, label: op })));
  const profileOptions = $derived(
    evalProfiles.map((p) => ({ value: p.uid, label: p.alias ?? p.name ?? p.uid.slice(0, 8) })),
  );
</script>

<div
  class="flex flex-wrap items-center gap-2 border-2 border-primary-800 bg-surface-50 rounded-base px-3 py-2 shadow-small"
>
  <div class="flex items-center gap-1 text-xs font-black uppercase tracking-widest text-primary-800">
    <Filter class="w-3 h-3" /> Filters
  </div>

  {#if evalProfiles.length > 0}
    <div class="flex items-center gap-1">
      <span class="text-xs font-bold uppercase tracking-wide text-primary-700">Profile</span>
      <CustomSelect
        label="Profile"
        options={profileOptions}
        value={applied.entity_id}
        disabled={lockEntity}
        onChange={(v) =>
          onChange({
            agent_name: applied.agent_name,
            model: applied.model,
            provider_name: applied.provider_name,
            operation_name: applied.operation_name,
            entity_id: v,
          })}
      />
    </div>
  {/if}

  <div class="flex items-center gap-1">
    <span class="text-xs font-bold uppercase tracking-wide text-primary-700">Agent</span>
    <CustomSelect
      label="Agent"
      options={agentOptions}
      value={applied.agent_name}
      onChange={(v) =>
        onChange({
          agent_name: v,
          model: applied.model,
          provider_name: applied.provider_name,
          operation_name: applied.operation_name,
          entity_id: applied.entity_id,
        })}
    />
  </div>

  <div class="flex items-center gap-1">
    <span class="text-xs font-bold uppercase tracking-wide text-primary-700">Model</span>
    <CustomSelect
      label="Model"
      options={modelOptions}
      value={applied.model}
      onChange={(v) =>
        onChange({
          agent_name: applied.agent_name,
          model: v,
          provider_name: applied.provider_name,
          operation_name: applied.operation_name,
          entity_id: applied.entity_id,
        })}
    />
  </div>

  <div class="flex items-center gap-1">
    <span class="text-xs font-bold uppercase tracking-wide text-primary-700">Provider</span>
    <CustomSelect
      label="Provider"
      options={providerOptions}
      value={applied.provider_name}
      onChange={(v) =>
        onChange({
          agent_name: applied.agent_name,
          model: applied.model,
          provider_name: v,
          operation_name: applied.operation_name,
          entity_id: applied.entity_id,
        })}
    />
  </div>

  <div class="flex items-center gap-1">
    <span class="text-xs font-bold uppercase tracking-wide text-primary-700">Operation</span>
    <CustomSelect
      label="Operation"
      options={operationOptions}
      value={applied.operation_name}
      onChange={(v) =>
        onChange({
          agent_name: applied.agent_name,
          model: applied.model,
          provider_name: applied.provider_name,
          operation_name: v,
          entity_id: applied.entity_id,
        })}
    />
  </div>
</div>
