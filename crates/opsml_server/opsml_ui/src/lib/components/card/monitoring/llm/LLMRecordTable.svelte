<script lang="ts">
  import { tick } from "svelte";
  import { type PaginationCursor, type LLMDriftServerRecord, type LLMPageResponse, type ServiceInfo, Status } from "../types";
  import { getLLMRecordPage } from "../util";
  import { ArrowLeft, ArrowRight } from 'lucide-svelte';
  import CodeModal from "../CodeModal.svelte";


let parentContainer: HTMLDivElement | null = null;

  function scrollParentToBottomOfWindow() {
    if (parentContainer) {
      parentContainer.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }

let { 
    space,
    name, 
    version,
    currentPage,
  } = $props<{
    space: string;
    name: string;
    version: string;
    currentPage: LLMPageResponse;
  }>();

    let paginationCursor = $state<PaginationCursor | undefined>(undefined);
    let cursorStack: (PaginationCursor | undefined)[] =$state([currentPage.next_cursor]);
    let pageItems: LLMDriftServerRecord[] = $state(currentPage.items);
    let has_more: boolean = $state(currentPage.has_more);
    let status = $state<Status | undefined>(undefined);
    let serviceInfo: ServiceInfo = $state({"space": space, "name": name, "version": version});
    let pageNbr: number = $state(1);

  // Function for getting next page
   async function changePage(newPage: number) {
  if (newPage > pageNbr) {
    // Going forward
    let next_page = await getLLMRecordPage(serviceInfo, status, cursorStack[pageNbr - 1]);
    pageItems = next_page.items;
    has_more = next_page.has_more;
    cursorStack.push(next_page.next_cursor);
    pageNbr = newPage;

  } else if (newPage < pageNbr && newPage > 0) {
    
    let prev_page;
    if (newPage === 1) {
      // First page: fetch with no cursor
      prev_page = await getLLMRecordPage(serviceInfo, status, undefined);
    } else {
      let prevCursor = cursorStack[newPage - 1];
      prev_page = await getLLMRecordPage(serviceInfo, status, prevCursor);
    }
    pageItems = prev_page.items;
    has_more = prev_page.has_more;
    cursorStack = cursorStack.slice(0, newPage);
    pageNbr = newPage;
  }

  await tick();
  scrollParentToBottomOfWindow();
}

</script>

<div class="flex flex-col h-full" bind:this={parentContainer}>
  <div class="items-center text-lg mr-2 font-bold text-primary-800">LLM Records</div>
  {#if pageItems.length === 0}
    <div class="flex items-center justify-center flex-1 text-center text-gray-500 text-lg text-primary-500 font-bold">
      No LLM Drift Records Found
    </div>
  {:else}
    <div class="overflow-auto w-full">
      <table class="text-black border-collapse text-sm bg-white w-full">
        <thead class="sticky top-0 z-10 bg-white" style="box-shadow: 0 2px 0 0 #000;">
          <tr>
            <th class="p-3 font-heading pl-6 text-left text-black">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                ID
              </span>
            </th>
            <th class="p-3 font-heading">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                Status
              </span>
            </th>
            <th class="p-3 font-heading">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                Score
              </span>
            </th>
            <th class="p-3 font-heading">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                Prompt
              </span>
            </th>
            <th class="p-3 font-heading">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                Context
              </span>
            </th>
            <th class="p-3 font-heading">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                Created At
              </span>
            </th>
            <th class="p-3 font-heading">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                Processing Duration
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          {#each pageItems as record, i}
            <tr class={`border-b-2 border-black hover:bg-primary-300 py-2 ${i % 2 === 0 ? 'bg-gray-100' : 'bg-white'}`}>
              <td class="p-3 pl-8">{record.id}</td>
              <td class="p-3 text-center">
                <span class={`px-2 py-1 rounded-full border border-black text-xs font-medium ${
                  record.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                  record.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                  record.status === 'processed' ? 'bg-green-100 text-green-800' :
                  record.status === 'failed' ? 'bg-red-100 text-red-800' :
                  'bg-primary-100 text-primary-800'
                }`}>
                  {record.status}
                </span>
              </td>
              <td class="p-3 text-center"><CodeModal name='Score' code={record.score} /></td>
              {#if record.prompt}
                <td class="p-3 text-center"><CodeModal name='Prompt' code={record.prompt} /></td>
                {:else}
                <td class="p-3 text-center"></td>
              {/if}
              {#if record.context}
                <td class="p-3 text-center"><CodeModal name='Context' code={record.context} /></td>
                {:else}
                <td class="p-3 text-center"></td>
              {/if}
              <td class="p-3 text-center">{record.created_at}</td>
              <td class="p-3 text-center">
                <span class="px-2 py-1 rounded-full border border-black text-xs font-medium">
                  {record.processing_duration !== undefined ? `${record.processing_duration / 1000} seconds` : 'N/A'}
                </span>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>


    <div class="flex justify-center pt-4 gap-2 border-t-2 border-black">
        {#if cursorStack.length > 1}
          <button
            class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9"
            onclick={() => changePage(pageNbr - 1)}
            aria-label="Previous Page"
          >
            <ArrowLeft color="#5948a3" />
          </button>
        {/if}

        <div class="flex bg-surface-50 border-black border-2 text-center items-center rounded-base px-2 shadow-small h-9">
          <span class="text-primary-800 mr-1 text-xs">{pageNbr}</span>
        </div>

        {#if has_more}
          <button
            class="btn bg-surface-50 border-black border-2 shadow-small shadow-hover-small h-9"
            onclick={() => changePage(pageNbr + 1)}
            aria-label="Next Page"
          >
            <ArrowRight color="#5948a3" />
          </button>
        {/if}
      </div>
  {/if}
</div>