<script lang="ts">
  import type { QueryPageResponse, CardCursor } from "$lib/components/card/types";
  import  { RegistryType } from "$lib/utils";
  import CardPage from "$lib/components/card/CardPage.svelte";
  import { ArrowLeft, ArrowRight } from 'lucide-svelte';

  let { registryPage, registry, onPageChange } = $props<{
    registryPage: QueryPageResponse;
    registry: RegistryType;
    onPageChange?: (cursor: CardCursor) => Promise<void>;
  }>();

  async function handleNextPage() {
    if (registryPage.next_cursor && onPageChange) {
      await onPageChange(registryPage.next_cursor);
    }
  }

  async function handlePreviousPage() {
    if (registryPage.previous_cursor && onPageChange) {
      await onPageChange(registryPage.previous_cursor);
    }
  }
</script>

<div class="pt-4">

  <div class="pt-4 grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-3 gap-2 justify-items-center">
    {#each registryPage.items as summary}
      <CardPage
        space={summary.space}
        name={summary.name}
        version={summary.version}
        nbr_versions={summary.versions}
        updated_at={summary.updated_at}
        registry={registry}
        bgColor={"bg-primary-400"}
      />
    {/each}
  </div>

  <!-- Pagination Controls -->
  <div class="flex justify-center pt-4 gap-2 items-center">
    {#if registryPage.has_previous}
      <button
        class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9"
        onclick={handlePreviousPage}
        disabled={!onPageChange}
      >
        <ArrowLeft color="#5948a3"/>
      </button>
    {/if}

    <div class="flex bg-surface-50 border-black border-2 text-center items-center rounded-base px-2 shadow-small h-9">
      <span class="text-primary-800 text-xs">
        {registryPage.page_info.page_size} items
        {#if registryPage.page_info.offset > 0}
          (offset: {registryPage.page_info.offset})
        {/if}
      </span>
    </div>

    {#if registryPage.has_next}
      <button
        class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9"
        onclick={handleNextPage}
        disabled={!onPageChange}
      >
        <ArrowRight color="#5948a3"/>
      </button>
    {/if}
  </div>
</div>