<script lang="ts">
  import type { GroupedMetrics, GroupedMetric, Experiment } from "./types";
  import { ArrowUpDown, ArrowUp, ArrowDown } from "lucide-svelte";

  let { groupedMetrics, currentVersion } = $props<{groupedMetrics: GroupedMetrics, selectedExperiments: Experiment[], currentVersion: string}>();

  type Row = {
    metricName: string;
    currentValue: number | null;
    comparedValue: number | null;
    comparedTo: string;
    difference: number | null;
    idx: number;
  };

  let sortColumn: keyof Row = $state("metricName");
  let sortDirection: "asc" | "desc" = $state("asc");

  function round(value: number | null): number | null {
    if (value === null) return null;
    return Number(value.toFixed(2));
  }

  // Helper to find the current version metric
  function getCurrentMetric(metrics: GroupedMetric[]): GroupedMetric | undefined {
    return metrics.find(m => m.version === currentVersion) ?? metrics[0];
  }

  // Build comparison rows
  const rows = $derived.by(() => {
    const result: Row[] = [];
    for (const [metricName, metrics] of Object.entries(groupedMetrics) as [string, GroupedMetric[]][]) {
      const currentMetric = getCurrentMetric(metrics);
      if (!currentMetric || !currentMetric.value) continue;

      for (const metric of metrics) {
        // Skip comparing current to itself
        if (metric.version === currentMetric.version) continue;

        // If length is 1, compare single value
        if (currentMetric.value.length === 1 && metric.value.length === 1) {
          result.push({
            metricName,
            currentValue: round(currentMetric.value[0]),
            comparedValue: round(metric.value[0]),
            comparedTo: metric.version,
            difference: round(currentMetric.value[0] - metric.value[0]),
            idx: 0,
          });
        } else {
          // If length > 1, compare by index
          for (let i = 0; i < currentMetric.value.length; i++) {
            const currentVal = currentMetric.value[i] ?? null;
            const comparedVal = metric.value[i] ?? null;
            result.push({
              metricName,
              currentValue: round(currentVal),
              comparedValue: round(comparedVal),
              comparedTo: metric.version,
              difference: (currentVal !== null && comparedVal !== null) ? round(currentVal - comparedVal) : null,
              idx: i,
            });
          }
        }
      }
    }
    return result;
  });

  // Sorting logic
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
</script>

<div class="h-full flex flex-col overflow-hidden">
  <div class="flex-1 overflow-auto">
    <table class="text-black border-collapse text-sm bg-white w-full">
      <thead class="sticky top-0 z-10 bg-white" style="box-shadow: 0 2px 0 0 #000;">
        <tr>
          <th class="p-3 font-heading pl-6 text-left cursor-pointer hover:bg-primary-50" onclick={() => setSort("metricName")}>
            <div class="flex gap-1 items-center">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>Name</span>
              <span class="ml-2 text-gray-400">
                {#if sortColumn === "metricName"}
                  {#if sortDirection === "asc"}
                    <ArrowUp color="#8059b6" size={16}/>
                  {:else}
                    <ArrowDown color="#8059b6" size={16}/>
                  {/if}
                {:else}
                  <ArrowUpDown color="#8059b6" size={16}/>
                {/if}
              </span>
            </div>
          </th>
          <th class="p-3 font-heading cursor-pointer text-center hover:bg-primary-50" onclick={() => setSort("currentValue")}>
            <div class="flex items-center justify-center gap-2">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>Current Value</span>
              <span class="ml-2 text-gray-400">
                {#if sortColumn === "currentValue"}
                  {#if sortDirection === "asc"}
                    <ArrowUp color="#8059b6" size={16}/>
                  {:else}
                    <ArrowDown color="#8059b6" size={16}/>
                  {/if}
                {:else}
                  <ArrowUpDown color="#8059b6" size={16}/>
                {/if}
              </span>
            </div>
          </th>
          <th class="p-3 font-heading cursor-pointer text-center hover:bg-primary-50" onclick={() => setSort("comparedValue")}>
            <div class="flex items-center justify-center gap-2">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>Compared Value</span>
              <span class="ml-2 text-gray-400">
                {#if sortColumn === "comparedValue"}
                  {#if sortDirection === "asc"}
                    <ArrowUp color="#8059b6" size={16}/>
                  {:else}
                    <ArrowDown color="#8059b6" size={16}/>
                  {/if}
                {:else}
                  <ArrowUpDown color="#8059b6" size={16}/>
                {/if}
              </span>
            </div>
          </th>
          <th class="p-3 font-heading cursor-pointer text-center hover:bg-primary-50" onclick={() => setSort("comparedTo")}>
            <div class="flex items-center justify-center gap-2">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>Compared To Version</span>
              <span class="ml-2 text-gray-400">
                {#if sortColumn === "comparedTo"}
                  {#if sortDirection === "asc"}
                    <ArrowUp color="#8059b6" size={16}/>
                  {:else}
                    <ArrowDown color="#8059b6" size={16}/>
                  {/if}
                {:else}
                  <ArrowUpDown color="#8059b6" size={16}/>
                {/if}
              </span>
            </div>
          </th>
          <th class="p-3 font-heading cursor-pointer text-center hover:bg-primary-50" onclick={() => setSort("difference")}>
            <div class="flex items-center justify-center gap-2">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>Difference</span>
              <span class="ml-2 text-gray-400">
                {#if sortColumn === "difference"}
                  {#if sortDirection === "asc"}
                    <ArrowUp color="#8059b6" size={16}/>
                  {:else}
                    <ArrowDown color="#8059b6" size={16}/>
                  {/if}
                {:else}
                  <ArrowUpDown color="#8059b6" size={16}/>
                {/if}
              </span>
            </div>
          </th>
          <th class="p-3 font-heading cursor-pointer text-center hover:bg-primary-50" onclick={() => setSort("idx")}>
            <div class="flex items-center justify-center gap-2">
              <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>Index</span>
              <span class="ml-2 text-gray-400">
                {#if sortColumn === "idx"}
                  {#if sortDirection === "asc"}
                    <ArrowUp color="#8059b6" size={16}/>
                  {:else}
                    <ArrowDown color="#8059b6" size={16}/>
                  {/if}
                {:else}
                  <ArrowUpDown color="#8059b6" size={16}/>
                {/if}
              </span>
            </div>
          </th>
        </tr>
      </thead>
      <tbody>
        {#each sortedRows as row, idx}
          <tr class={`border-b-2 border-black hover:bg-primary-300 py-2 ${idx % 2 === 0 ? 'bg-gray-100' : 'bg-white'}`}>
            <td class="p-3 pl-6">{row.metricName}</td>
            <td class="p-3 text-center">{row.currentValue ?? "-"}</td>
            <td class="p-3 text-center">{row.comparedValue ?? "-"}</td>
            <td class="p-3 text-center">{row.comparedTo}</td>
            <td class="p-3 text-center">
              {#if row.difference !== null}
                <span
                  class={`px-2 py-1 rounded-full border text-xs font-medium
                    ${row.difference > 0
                      ? 'border-green-800 bg-green-100 text-green-800'
                      : row.difference < 0
                        ? 'border-red-800 bg-red-100 text-red-800'
                        : 'border-blue-800 bg-blue-100 text-blue-800'
                    }`
                  }
                >
                  {row.difference}
                </span>
              {:else}
                <span class="px-2 py-1 rounded-full border text-xs font-medium border-blue-800 bg-blue-100 text-blue-800">
                  -
                </span>
              {/if}
            </td>
            <td class="p-3 text-center">{row.idx}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>