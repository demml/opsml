<script lang="ts">
  // Scouter currently returns facet counts for services and status codes only.
  // Namespace/version/instance/error/duration/attribute controls update the clause directly.
  import type { FacetCount, TracePageFilter } from "../types";
  import AttributeFacet from "./AttributeFacet.svelte";
  import DurationFacet from "./DurationFacet.svelte";
  import FacetRow from "./FacetRow.svelte";
  import FacetSection from "./FacetSection.svelte";
  import { findClauses } from "../clause";

  let {
    filters,
    services,
    namespaces,
    versions,
    instances,
    statuses,
    onSetService,
    onClearService,
    onSetNamespace,
    onClearNamespace,
    onSetVersion,
    onClearVersion,
    onSetInstance,
    onClearInstance,
    onSetStatus,
    onClearStatus,
    onToggleErrors,
    onSetDuration,
    onSetAttributes,
  } = $props<{
    filters: TracePageFilter;
    services: FacetCount[];
    namespaces: FacetCount[];
    versions: FacetCount[];
    instances: FacetCount[];
    statuses: FacetCount[];
    onSetService: (service: string) => void;
    onClearService: () => void;
    onSetNamespace: (namespace: string) => void;
    onClearNamespace: () => void;
    onSetVersion: (version: string) => void;
    onClearVersion: () => void;
    onSetInstance: (instance: string) => void;
    onClearInstance: () => void;
    onSetStatus: (status: number) => void;
    onClearStatus: () => void;
    onToggleErrors: (next: boolean) => void;
    onSetDuration: (next: { min?: number; max?: number }) => void;
    onSetAttributes: (next: string[]) => void;
  }>();

  const selectedService = $derived(findClauses(filters.filters.clause, "service")[0]?.value);
  const selectedStatusCode = $derived(findClauses(filters.filters.clause, "status_code")[0]?.value);
  const selectedNamespace = $derived(findClauses(filters.filters.clause, "service_namespace")[0]?.value);
  const selectedVersion = $derived(findClauses(filters.filters.clause, "service_version")[0]?.value);
  const selectedInstance = $derived(findClauses(filters.filters.clause, "service_instance_id")[0]?.value);
  const selectedHasErrors = $derived(findClauses(filters.filters.clause, "has_errors")[0]?.value);
  const selectedMinDuration = $derived(findClauses(filters.filters.clause, "duration_min_ms")[0]?.value);
  const selectedMaxDuration = $derived(findClauses(filters.filters.clause, "duration_max_ms")[0]?.value);
  const selectedAttributes = $derived(
    findClauses(filters.filters.clause, "attr").map(
      (clause) => `${clause.value.key}=${clause.value.value}`,
    ),
  );

  let namespaceInput = $state("");
  let versionInput = $state("");
  let instanceInput = $state("");

  $effect(() => {
    namespaceInput = selectedNamespace ?? "";
    versionInput = selectedVersion ?? "";
    instanceInput = selectedInstance ?? "";
  });

  function applyNamespaceInput() {
    const next = namespaceInput.trim();
    if (next) onSetNamespace(next);
    else onClearNamespace();
  }

  function applyVersionInput() {
    const next = versionInput.trim();
    if (next) onSetVersion(next);
    else onClearVersion();
  }

  function applyInstanceInput() {
    const next = instanceInput.trim();
    if (next) onSetInstance(next);
    else onClearInstance();
  }
</script>

<aside class="flex flex-col rounded-base border-2 border-black shadow bg-white overflow-hidden self-start">
  <div class="px-3 py-2 border-b-2 border-black bg-primary-500">
    <span class="text-xs font-black uppercase tracking-widest text-white">Filters</span>
  </div>

  <FacetSection label="Status">
    <FacetRow
      label="Any"
      selected={selectedStatusCode === undefined}
      onSelect={onClearStatus}
    />
    {#each statuses as s (s.value)}
      <FacetRow
        label={s.value}
        count={s.count}
        selected={String(selectedStatusCode) === s.value}
        onSelect={() => onSetStatus(Number(s.value))}
      />
    {/each}
  </FacetSection>

  <FacetSection label="Service">
    <FacetRow
      label="Any"
      selected={selectedService === undefined}
      onSelect={onClearService}
    />
    {#each services as service (service.value)}
      <FacetRow
        label={service.value}
        count={service.count}
        selected={selectedService === service.value}
        onSelect={() => onSetService(service.value)}
      />
    {/each}
  </FacetSection>

  <FacetSection label="Namespace">
    <FacetRow
      label="Any"
      selected={selectedNamespace === undefined}
      onSelect={onClearNamespace}
    />
    {#each namespaces as namespace (namespace.value)}
      <FacetRow
        label={namespace.value}
        count={namespace.count}
        selected={selectedNamespace === namespace.value}
        onSelect={() => onSetNamespace(namespace.value)}
      />
    {/each}
    {#if namespaces.length === 0}
      <div class="space-y-2">
        <input
          type="text"
          bind:value={namespaceInput}
          placeholder="namespace"
          class="w-full px-2 py-1 text-xs font-mono border-2 border-black bg-white text-primary-800 rounded-base"
        />
        <div class="flex items-center gap-2">
          <button
            type="button"
            onclick={applyNamespaceInput}
            class="px-2 py-1 text-xs font-black uppercase tracking-wide border-2 border-black bg-primary-500 text-white rounded-base shadow-small"
          >
            Apply
          </button>
          <button
            type="button"
            onclick={onClearNamespace}
            class="px-2 py-1 text-xs font-bold border-2 border-black bg-surface-50 text-primary-800 rounded-base shadow-small"
          >
            Clear
          </button>
        </div>
      </div>
    {/if}
  </FacetSection>

  <FacetSection label="Version">
    <FacetRow
      label="Any"
      selected={selectedVersion === undefined}
      onSelect={onClearVersion}
    />
    {#each versions as version (version.value)}
      <FacetRow
        label={version.value}
        count={version.count}
        selected={selectedVersion === version.value}
        onSelect={() => onSetVersion(version.value)}
      />
    {/each}
    {#if versions.length === 0}
      <div class="space-y-2">
        <input
          type="text"
          bind:value={versionInput}
          placeholder="version"
          class="w-full px-2 py-1 text-xs font-mono border-2 border-black bg-white text-primary-800 rounded-base"
        />
        <div class="flex items-center gap-2">
          <button
            type="button"
            onclick={applyVersionInput}
            class="px-2 py-1 text-xs font-black uppercase tracking-wide border-2 border-black bg-primary-500 text-white rounded-base shadow-small"
          >
            Apply
          </button>
          <button
            type="button"
            onclick={onClearVersion}
            class="px-2 py-1 text-xs font-bold border-2 border-black bg-surface-50 text-primary-800 rounded-base shadow-small"
          >
            Clear
          </button>
        </div>
      </div>
    {/if}
  </FacetSection>

  <FacetSection label="Instance" defaultOpen={false}>
    <FacetRow
      label="Any"
      selected={selectedInstance === undefined}
      onSelect={onClearInstance}
    />
    {#each instances as instance (instance.value)}
      <FacetRow
        label={instance.value}
        count={instance.count}
        selected={selectedInstance === instance.value}
        onSelect={() => onSetInstance(instance.value)}
      />
    {/each}
    {#if instances.length === 0}
      <div class="space-y-2">
        <input
          type="text"
          bind:value={instanceInput}
          placeholder="instance id"
          class="w-full px-2 py-1 text-xs font-mono border-2 border-black bg-white text-primary-800 rounded-base"
        />
        <div class="flex items-center gap-2">
          <button
            type="button"
            onclick={applyInstanceInput}
            class="px-2 py-1 text-xs font-black uppercase tracking-wide border-2 border-black bg-primary-500 text-white rounded-base shadow-small"
          >
            Apply
          </button>
          <button
            type="button"
            onclick={onClearInstance}
            class="px-2 py-1 text-xs font-bold border-2 border-black bg-surface-50 text-primary-800 rounded-base shadow-small"
          >
            Clear
          </button>
        </div>
      </div>
    {/if}
  </FacetSection>

  <FacetSection label="Errors only">
    <label class="flex items-center gap-2 text-xs text-primary-800 cursor-pointer">
      <input
        type="checkbox"
        checked={selectedHasErrors === true}
        onchange={(event) =>
          onToggleErrors((event.currentTarget as HTMLInputElement).checked)}
        class="w-4 h-4 border-2 border-black bg-surface-50 accent-primary-500"
      />
      <span class="font-mono">Show only errored traces</span>
    </label>
  </FacetSection>

  <FacetSection label="Duration" defaultOpen={false}>
    <DurationFacet
      min={selectedMinDuration}
      max={selectedMaxDuration}
      onApply={onSetDuration}
    />
  </FacetSection>

  <FacetSection label="Attributes" defaultOpen={false}>
    <AttributeFacet
      items={selectedAttributes}
      onChange={onSetAttributes}
    />
  </FacetSection>
</aside>
