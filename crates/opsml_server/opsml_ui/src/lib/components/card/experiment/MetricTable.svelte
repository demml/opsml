<script lang="ts">
  import type { GroupedMetrics, GroupedMetric } from "./types";

  export let groupedMetrics: GroupedMetrics;
</script>

<div class="flex flex-col h-full">
  <div class="overflow-auto w-full">
    <table class="text-black border-collapse text-sm bg-white w-full">
      <thead class="sticky top-0 z-10 bg-white" style="box-shadow: 0 2px 0 0 #000;">
        <tr>
          <th class="p-3 font-heading pl-6 text-left text-black">
            <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>Name</span>
          </th>
          <th class="p-3 font-heading">
            <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>Value</span>
          </th>
          <th class="p-3 font-heading">
            <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>Version</span>
          </th>
          <th class="p-3 font-heading">
            <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>Step</span>
          </th>
          <th class="p-3 font-heading">
            <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>Timestamp</span>
          </th>
        </tr>
      </thead>
      <tbody>
        {#each Object.entries(groupedMetrics) as [metricName, metrics]: [string, GroupedMetric[]]}
          {#each metrics as metric}
            {#each metric.value as value, idx}
              <tr class={`border-b-2 border-black hover:bg-primary-300 py-2 ${idx % 2 === 0 ? 'bg-gray-100' : 'bg-white'}`}>
                <td class="p-3 pl-6">
                  <span class="font-semibold">{metricName}</span>
                </td>
                <td class="p-3 p-3 text-center">{value}</td>
                <td class="p-3 text-center">{metric.version}</td>
                <td class="p-3 text-center">{metric.step ? metric.step[idx] : ''}</td>
                <td class="p-3 text-center">{metric.timestamp ? metric.timestamp[idx] : ''}</td>
              </tr>
            {/each}
          {/each}
        {/each}
      </tbody>
    </table>
  </div>
</div>