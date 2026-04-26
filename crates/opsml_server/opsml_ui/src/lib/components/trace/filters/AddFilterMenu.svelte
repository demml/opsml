<script lang="ts">
  import type { FacetCount } from "../types";

  let {
    services,
    statuses,
    onClose,
    onAddService,
    onAddStatus,
    onAddHasErrors,
    onAddAttribute,
    onAddDuration,
  } = $props<{
    services: FacetCount[];
    statuses: FacetCount[];
    onClose: () => void;
    onAddService: (service: string) => void;
    onAddStatus: (status: number) => void;
    onAddHasErrors: () => void;
    onAddAttribute: (raw: string) => void;
    onAddDuration: (min?: number, max?: number) => void;
  }>();

  type MenuSection = "service" | "status" | "duration" | "attribute" | null;
  let activeSection = $state<MenuSection>(null);
  let attributeInput = $state("");
  let durationMin = $state("");
  let durationMax = $state("");

  const topServices = $derived(services.slice(0, 6));
  const topStatuses = $derived(statuses.slice(0, 6));

  function selectService(service: string) {
    onAddService(service);
    onClose();
  }

  function selectStatus(status: string) {
    const next = Number(status);
    if (!Number.isNaN(next)) {
      onAddStatus(next);
    }
    onClose();
  }

  function addErrorsOnly() {
    onAddHasErrors();
    onClose();
  }

  function submitAttribute() {
    const trimmed = attributeInput.trim();
    if (!trimmed) return;
    onAddAttribute(trimmed);
    attributeInput = "";
    onClose();
  }

  function submitDuration() {
    const parsedMin = durationMin.trim() === "" ? undefined : Number(durationMin);
    const parsedMax = durationMax.trim() === "" ? undefined : Number(durationMax);

    const min =
      parsedMin !== undefined && !Number.isNaN(parsedMin) ? parsedMin : undefined;
    const max =
      parsedMax !== undefined && !Number.isNaN(parsedMax) ? parsedMax : undefined;

    onAddDuration(min, max);
    onClose();
  }
</script>

<button
  type="button"
  class="fixed inset-0 z-20 cursor-default"
  aria-label="Close add filter menu"
  onclick={onClose}
></button>

<div class="absolute right-0 mt-1 w-72 z-30 border-2 border-black bg-white rounded-base shadow p-2 space-y-1">
  <button
    type="button"
    class="w-full flex items-center justify-between px-2 py-1 text-xs hover:bg-primary-100 cursor-pointer rounded-base"
    onclick={() => (activeSection = activeSection === "service" ? null : "service")}
  >
    <span class="font-black uppercase tracking-wide text-primary-800">Service</span>
    <span class="font-mono text-[10px] text-gray-500">pick…</span>
  </button>
  {#if activeSection === "service"}
    <div class="space-y-1 px-1 pb-1">
      {#if topServices.length === 0}
        <p class="text-[10px] font-mono text-gray-500 px-1 py-1">No services found</p>
      {:else}
        {#each topServices as service (service.value)}
          <button
            type="button"
            class="w-full flex items-center justify-between px-2 py-1 text-xs border border-black rounded-base bg-surface-50 hover:bg-primary-100 transition-colors duration-100"
            onclick={() => selectService(service.value)}
          >
            <span class="font-mono truncate">{service.value}</span>
            <span class="text-[10px] text-gray-500 font-mono">{service.count}</span>
          </button>
        {/each}
      {/if}
    </div>
  {/if}

  <button
    type="button"
    class="w-full flex items-center justify-between px-2 py-1 text-xs hover:bg-primary-100 cursor-pointer rounded-base"
    onclick={() => (activeSection = activeSection === "status" ? null : "status")}
  >
    <span class="font-black uppercase tracking-wide text-primary-800">Status</span>
    <span class="font-mono text-[10px] text-gray-500">2xx/4xx/5xx</span>
  </button>
  {#if activeSection === "status"}
    <div class="space-y-1 px-1 pb-1">
      {#if topStatuses.length === 0}
        <p class="text-[10px] font-mono text-gray-500 px-1 py-1">No statuses found</p>
      {:else}
        {#each topStatuses as status (status.value)}
          <button
            type="button"
            class="w-full flex items-center justify-between px-2 py-1 text-xs border border-black rounded-base bg-surface-50 hover:bg-primary-100 transition-colors duration-100"
            onclick={() => selectStatus(status.value)}
          >
            <span class="font-mono">{status.value}</span>
            <span class="text-[10px] text-gray-500 font-mono">{status.count}</span>
          </button>
        {/each}
      {/if}
    </div>
  {/if}

  <button
    type="button"
    class="w-full flex items-center justify-between px-2 py-1 text-xs hover:bg-primary-100 cursor-pointer rounded-base"
    onclick={addErrorsOnly}
  >
    <span class="font-black uppercase tracking-wide text-primary-800">Has errors</span>
    <span class="font-mono text-[10px] text-gray-500">boolean</span>
  </button>

  <button
    type="button"
    class="w-full flex items-center justify-between px-2 py-1 text-xs hover:bg-primary-100 cursor-pointer rounded-base"
    onclick={() => (activeSection = activeSection === "duration" ? null : "duration")}
  >
    <span class="font-black uppercase tracking-wide text-primary-800">Duration</span>
    <span class="font-mono text-[10px] text-gray-500">min/max ms</span>
  </button>
  {#if activeSection === "duration"}
    <div class="space-y-2 px-1 pb-1">
      <div class="grid grid-cols-2 gap-2">
        <input
          type="number"
          min="0"
          step="1"
          bind:value={durationMin}
          placeholder="min ms"
          class="w-full px-2 py-1 text-xs font-mono border-2 border-black rounded-base bg-white"
        />
        <input
          type="number"
          min="0"
          step="1"
          bind:value={durationMax}
          placeholder="max ms"
          class="w-full px-2 py-1 text-xs font-mono border-2 border-black rounded-base bg-white"
        />
      </div>
      <button
        type="button"
        class="w-full px-2 py-1 text-xs font-black uppercase tracking-wide border-2 border-black bg-primary-500 text-white rounded-base shadow-small"
        onclick={submitDuration}
      >
        Apply
      </button>
    </div>
  {/if}

  <button
    type="button"
    class="w-full flex items-center justify-between px-2 py-1 text-xs hover:bg-primary-100 cursor-pointer rounded-base"
    onclick={() => (activeSection = activeSection === "attribute" ? null : "attribute")}
  >
    <span class="font-black uppercase tracking-wide text-primary-800">Attribute</span>
    <span class="font-mono text-[10px] text-gray-500">key=value</span>
  </button>
  {#if activeSection === "attribute"}
    <div class="space-y-1 px-1 pb-1">
      <input
        type="text"
        bind:value={attributeInput}
        placeholder="user.id=42"
        class="w-full px-2 py-1 text-xs font-mono border-2 border-black rounded-base bg-white"
        onkeydown={(event) => event.key === "Enter" && submitAttribute()}
      />
    </div>
  {/if}
</div>
