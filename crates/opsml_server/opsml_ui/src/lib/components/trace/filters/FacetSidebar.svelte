<script lang="ts">
  import type { FacetCount, TracePageFilter } from "../types";
  import AttributeFacet from "./AttributeFacet.svelte";
  import DurationFacet from "./DurationFacet.svelte";
  import FacetRow from "./FacetRow.svelte";
  import FacetSection from "./FacetSection.svelte";

  let {
    filters,
    services,
    statuses,
    onSetService,
    onClearService,
    onSetStatus,
    onClearStatus,
    onToggleErrors,
    onSetDuration,
    onSetAttributes,
  } = $props<{
    filters: TracePageFilter;
    services: FacetCount[];
    statuses: FacetCount[];
    onSetService: (service: string) => void;
    onClearService: () => void;
    onSetStatus: (status: number) => void;
    onClearStatus: () => void;
    onToggleErrors: (next: boolean) => void;
    onSetDuration: (next: { min?: number; max?: number }) => void;
    onSetAttributes: (next: string[]) => void;
  }>();
</script>

<aside class="flex flex-col rounded-base border-2 border-black shadow bg-white overflow-hidden self-start">
  <div class="px-3 py-2 border-b-2 border-black bg-primary-500">
    <span class="text-xs font-black uppercase tracking-widest text-white">Filters</span>
  </div>

  <FacetSection label="Status">
    <FacetRow
      label="Any"
      selected={filters.filters.status_code === undefined}
      onSelect={onClearStatus}
    />
    {#each statuses as s (s.value)}
      <FacetRow
        label={s.value}
        count={s.count}
        selected={String(filters.filters.status_code) === s.value}
        onSelect={() => onSetStatus(Number(s.value))}
      />
    {/each}
  </FacetSection>

  <FacetSection label="Service">
    <FacetRow
      label="Any"
      selected={filters.filters.service_name === undefined}
      onSelect={onClearService}
    />
    {#each services as service (service.value)}
      <FacetRow
        label={service.value}
        count={service.count}
        selected={filters.filters.service_name === service.value}
        onSelect={() => onSetService(service.value)}
      />
    {/each}
  </FacetSection>

  <FacetSection label="Errors only">
    <label class="flex items-center gap-2 text-xs text-primary-800 cursor-pointer">
      <input
        type="checkbox"
        checked={filters.filters.has_errors === true}
        onchange={(event) =>
          onToggleErrors((event.currentTarget as HTMLInputElement).checked)}
        class="w-4 h-4 border-2 border-black bg-surface-50 accent-primary-500"
      />
      <span class="font-mono">Show only errored traces</span>
    </label>
  </FacetSection>

  <FacetSection label="Duration" defaultOpen={false}>
    <DurationFacet
      min={filters.filters.duration_min_ms}
      max={filters.filters.duration_max_ms}
      onApply={onSetDuration}
    />
  </FacetSection>

  <FacetSection label="Attributes" defaultOpen={false}>
    <AttributeFacet
      items={filters.filters.attribute_filters ?? []}
      onChange={onSetAttributes}
    />
  </FacetSection>
</aside>
