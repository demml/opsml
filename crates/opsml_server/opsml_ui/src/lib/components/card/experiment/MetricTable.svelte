<script lang="ts">

  import type { GroupedMetrics, GroupedMetric } from "./types";
  import { ArrowUpDown, ArrowUp, ArrowDown } from "lucide-svelte";
  let { groupedMetrics} = $props<{groupedMetrics: GroupedMetrics}>();


  type Row = {
    metricName: string;
    value: number;
    version: string;
    step: number | null;
    timestamp: number | null;
  };

  let sortColumn: keyof Row = $state("value");
  let sortDirection: "asc" | "desc" = $state("asc");

  // Parse grouped metrics into rows
  const rows = $derived.by(() => {
    const result: Row[] = [];
    for (const [metricName, metrics] of Object.entries(groupedMetrics) as [string, GroupedMetric[]][]) {
      for (const metric of metrics) {
        if (metric.value && metric.value.length > 0) {
          for (let i = 0; i < metric.value.length; i++) {
            result.push({
              metricName,
              value: metric.value[i],
              version: metric.version,
              step: metric.step ? metric.step[i] : null,
              timestamp: metric.timestamp ? metric.timestamp[i] : null,
            });
          }
        }
      }
    }
    return result;
  });

  // Sorted rows - reactive to rows, sortColumn, and sortDirection changes
  const sortedRows = $derived.by(() => {
    return [...rows].sort((a, b) => {
      const aValue = a[sortColumn];
      const bValue = b[sortColumn];
      if (aValue === bValue) return 0;
      if (aValue === null) return 1;
      if (bValue === null) return -1;
      return (aValue < bValue ? -1 : 1) * (sortDirection === "asc" ? 1 : -1);
    });
  });

  function setSort(column: keyof Row) {
    if (sortColumn === column) {
      sortDirection = sortDirection === "asc" ? "desc" : "asc";
    } else {
      sortColumn = column;
      sortDirection = "asc";
    }
  }

  function getSortIcon(column: keyof Row): string {
    if (sortColumn === column) {
      return sortDirection === "asc" ? "▲" : "▼";
    }
    return "o" // Up-down arrow to indicate sortable
  }

</script>

<div class="h-full flex flex-col overflow-hidden">
  <div class="flex-1 overflow-auto">
    <table class="text-black border-collapse text-sm bg-white w-full">
      <thead class="sticky top-0 z-10 bg-white" style="box-shadow: 0 2px 0 0 #000;">
        <tr>
          <th class="p-3 font-heading pl-6 text-left text-black cursor-pointer hover:bg-primary-50 transition-colors" onclick={() => setSort("metricName")}>
            <div class="flex gap-1">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>Name</span>
              <span class="ml-2 text-gray-400 hover:text-gray-600">
                {#if sortColumn === "metricName"}
                  {#if sortDirection === "asc"}
                    <ArrowUp color="#8059b6" />
                  {:else}
                    <ArrowDown color="#8059b6" />
                  {/if}
                {:else}
                  <ArrowUpDown color="#8059b6" />
                {/if}
              </span>
            </div>
          </th>
          <th class="p-3 font-heading cursor-pointer text-center hover:bg-primary-50 transition-colors" onclick={() => setSort("value")}>
            <div class="flex items-center justify-center gap-2">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>Value</span>
              <span class="ml-2 text-gray-400 hover:text-gray-600">
                {#if sortColumn === "value"}
                  {#if sortDirection === "asc"}
                    <ArrowUp color="#8059b6" />
                  {:else}
                    <ArrowDown color="#8059b6" />
                  {/if}
                {:else}
                  <ArrowUpDown color="#8059b6" />
                {/if}
              </span>
            </div>
          </th>
          <th class="p-3 font-heading cursor-pointer text-center hover:bg-primary-50 transition-colors" onclick={() => setSort("version")}>
            <div class="flex items-center justify-center gap-2">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>Version</span>
              <span class="ml-2 text-gray-400 hover:text-gray-600">
                {#if sortColumn === "version"}
                  {#if sortDirection === "asc"}
                    <ArrowUp color="#8059b6" />
                  {:else}
                    <ArrowDown color="#8059b6" />
                  {/if}
                {:else}
                  <ArrowUpDown color="#8059b6" />
                {/if}
              </span>
            </div>
          </th>
          <th class="p-3 font-heading cursor-pointer text-center hover:bg-primary-50 transition-colors" onclick={() => setSort("step")}>
            <div class="flex items-center justify-center gap-2">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>Step</span>
              <span class="ml-2 text-gray-400 hover:text-gray-600">
                {#if sortColumn === "step"}
                  {#if sortDirection === "asc"}
                    <ArrowUp color="#8059b6" />
                  {:else}
                    <ArrowDown color="#8059b6" />
                  {/if}
                {:else}
                  <ArrowUpDown color="#8059b6" />
                {/if}
              </span>
            </div>
          </th>
          <th class="p-3 font-heading cursor-pointer text-center hover:bg-primary-50 transition-colors" onclick={() => setSort("timestamp")}>
            <div class="flex items-center justify-center gap-2">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>Timestamp</span>
              <span class="ml-2 text-gray-400 hover:text-gray-600">
                {#if sortColumn === "timestamp"}
                  {#if sortDirection === "asc"}
                    <ArrowUp color="#8059b6" />
                  {:else}
                    <ArrowDown color="#8059b6" />
                  {/if}
                {:else}
                  <ArrowUpDown color="#8059b6" />
                {/if}
              </span>
            </div>
          </th>
        </tr>
      </thead>
      <tbody>
        {#each sortedRows as row, idx}
          <tr class={`border-b-2 border-black hover:bg-primary-300 py-2 ${idx % 2 === 0 ? 'bg-gray-100' : 'bg-white'}`}>
            <td class="p-3 pl-6">
              <span class="font-semibold">{row.metricName}</span>
            </td>
            <td class="p-3 text-center">{row.value}</td>
            <td class="p-3 text-center">{row.version}</td>
            <td class="p-3 text-center">{row.step ?? ""}</td>
            <td class="p-3 text-center">{row.timestamp ?? ""}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>