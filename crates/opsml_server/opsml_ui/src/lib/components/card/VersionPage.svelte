<script lang="ts">
  import type { VersionPageResponse, RegistryStatsResponse } from "$lib/components/card/types";
  import type { RegistryType } from "$lib/utils";
  import { Settings, ArrowLeft, ArrowRight } from 'lucide-svelte';
  import VersionButton from "./VersionButton.svelte";
  import { getVersionPageWithCursor } from "../api/registry";

  let { registry, versionPage, cardRegistryStats } = $props<{
      registry: RegistryType,
      versionPage: VersionPageResponse,
      cardRegistryStats: RegistryStatsResponse
  }>();

  // registry-specific state
  let registryPage = $state<VersionPageResponse>(versionPage);
  let registryStats = $state<RegistryStatsResponse>(cardRegistryStats);

  async function handleNextPage() {
    if (registryPage.next_cursor) {
      registryPage = await getVersionPageWithCursor(fetch, registry, registryPage.next_cursor);
    }
  }

  async function handlePreviousPage() {
    if (registryPage.previous_cursor) {
      registryPage = await getVersionPageWithCursor(fetch, registry, registryPage.previous_cursor);
    }
  }

  function getPageRange(): string {
    const currentOffset = registryPage.previous_cursor
      ? registryPage.previous_cursor.offset + registryPage.previous_cursor.limit
      : 0;
    const start = currentOffset + 1;
    const end = currentOffset + registryPage.items.length;
    return `${start}-${end}`;
  }
</script>

<div class="flex-1 mx-auto w-10/12 pb-10 flex justify-center overflow-auto px-4 pt-4">
  <div class="grid grid-cols-1 w-full">
    <div class="col-span-1 md:col-span-4 gap-1 p-4 flex flex-col rounded-base border-primary-500 border-2 shadow-primary bg-surface-50 h-auto">
      <!-- Header -->
      <div class="flex flex-row items-center gap-2 pb-2">
        <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
          <Settings color="#40328b" />
        </div>
        <h2 class="font-bold text-primary-800 text-lg">Artifacts</h2>
      </div>

      <!-- Stats -->
      <div class="flex flex-row flex-wrap gap-1 items-center">
        <div>
          <span class="badge text-sm text-primary-800 border-black border-1 shadow-small bg-surface-50">
            {registryStats.stats.nbr_names} artifacts
          </span>
        </div>
        <div>
          <span class="badge text-sm text-primary-800 border-black border-1 shadow-small bg-surface-50">
            {registryStats.stats.nbr_versions} versions
          </span>
        </div>
        <div>
          <span class="badge text-sm text-primary-800 border-black border-1 shadow-small bg-surface-50">
            {registryStats.stats.nbr_spaces} spaces
          </span>
        </div>
      </div>

      <!-- Version Grid -->
      <div class="pt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4 gap-4 justify-items-center">
        {#each registryPage.items as summary}
          <VersionButton
            space={summary.space}
            name={summary.name}
            version={summary.version}
            updated_at={summary.created_at}
            registry={registry}
            bgColor={"bg-primary-400"}
          />
        {/each}
      </div>

      <!-- Pagination Controls (matching CardPageView/CardTableView style) -->
      <div class="flex justify-center pt-4 gap-2 items-center">
        {#if registryPage.has_previous}
          <button
            class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9"
            onclick={handlePreviousPage}
          >
            <ArrowLeft color="#5948a3"/>
          </button>
        {/if}

        <div class="flex bg-surface-50 border-black border-2 text-center items-center rounded-base px-2 shadow-small h-9">
          <span class="text-primary-800 text-xs font-medium">
            {getPageRange()}
          </span>
        </div>

        {#if registryPage.has_next}
          <button
            class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9"
            onclick={handleNextPage}
          >
            <ArrowRight color="#5948a3"/>
          </button>
        {/if}
      </div>
    </div>
  </div>
</div>