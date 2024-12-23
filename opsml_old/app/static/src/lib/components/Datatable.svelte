<script lang="ts">
	//Import local datatable components
	import ThSort from '$lib/components/ThSort.svelte';
	import ThFilter from '$lib/components/ThFilter.svelte';
	import Search from '$lib/components/Search.svelte';
	import RowsPerPage from '$lib/components/RowsPerPage.svelte';
	import RowCount from '$lib/components/RowCount.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
    import {type Metric, type Parameter} from '$lib/scripts/types';

	//Import handler from SSD
	import { DataHandler } from '@vincjo/datatables';

    export let data: Metric[] | Parameter[];
	export let forMetric: boolean = false;
	export let label: string = 'Metrics';

	//Init data handler - CLIENT
	const handler = new DataHandler(data, { rowsPerPage: 5 });
	const rows = handler.getRows();
</script>

<div class="overflow-x-auto space-y-4">
	<!-- Header -->
	<header class="flex justify-between gap-4">
		<div class="text-lg font-bold mt-6">{label}</div>
		<RowsPerPage {handler} />
	</header>
	<!-- Table -->
	<table class="table table-hover table-compact table-auto">
		<thead>
			<tr>
				<ThSort {handler} orderBy="name">Name</ThSort>
				<ThSort {handler} orderBy="value">Value</ThSort>

				{#if forMetric}
					<ThSort {handler} orderBy="step">Step</ThSort>
					<ThSort {handler} orderBy="timestamp">Timestamp</ThSort>
				{/if}
				
			</tr>
			<tr>
				<ThFilter {handler} filterBy="name" />
				<ThFilter {handler} filterBy="value" />

				{#if forMetric}
					<ThFilter {handler} filterBy="step" />
					<ThFilter {handler} filterBy="timestamp" />
				{/if}
			</tr>
		</thead>
		<tbody>
			{#each $rows as row}
				<tr>
					<td>{row.name}</td>
					<td class="text-center">{row.value}</td>

					{#if forMetric}
						<td class="text-center">{row.step}</td>
						<td class="text-center">{row.timestamp}</td>
					{/if}
				</tr>
			{/each}
		</tbody>
	</table>
	<!-- Footer -->
	<footer class="flex justify-between">
		<RowCount {handler} />
		<Pagination {handler} />
	</footer>
</div>



