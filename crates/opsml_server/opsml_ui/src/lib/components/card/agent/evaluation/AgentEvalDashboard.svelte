<!--
  AgentEvalDashboard.svelte
  ─────────────────────────
  Unified evaluation dashboard for an agent card. Shows:
    1. Agent identity header
    2. Aggregate overview stats
    3. Single combined workflow metric chart across all prompt cards
    4. Paginated evaluation records table (AgentEvalRecordTable)
    5. Paginated workflow results table (AgentEvalWorkflowTable)

  Pagination: each prompt card carries its own cursor inside monitoringData.
  When a user pages, all evals that have a cursor in that direction advance
  together. When the time range changes, performRefresh() runs without cursors,
  resetting pagination automatically.
-->
<script lang="ts">
  import type { AgentPromptEvalData, AgentRecordPage, AgentWorkflowPage } from './types';
  import type { RecordWithAgent, WorkflowWithAgent } from './types';
  import type { GenAIEvalProfile } from '$lib/components/scouter/genai/types';
  import AgentEvalOverview from './AgentEvalOverview.svelte';
  import AgentEvalRecordTable from './AgentEvalRecordTable.svelte';
  import AgentEvalWorkflowTable from './AgentEvalWorkflowTable.svelte';
  import { refreshGenAIMonitoringData } from '$lib/components/scouter/dashboard/utils';
  import { timeRangeState } from '$lib/components/utils/timeState.svelte';
  import { getRegistryPath, RegistryType, getMaxDataPoints } from '$lib/utils';
  import { generateColors } from '$lib/components/viz/utils';
  import { Chart } from 'chart.js/auto';
  import { Filler } from 'chart.js';
  import zoomPlugin from 'chartjs-plugin-zoom';
  import annotationPlugin from 'chartjs-plugin-annotation';
  import 'chartjs-adapter-date-fns';
  import { onMount, onDestroy } from 'svelte';
  import {
    Bot, TableProperties, ArrowRightLeft,
    Loader2, TrendingUp, KeySquare
  } from 'lucide-svelte';

  interface Props {
    agentName: string;
    agentVersion: string;
    agentPromptEvals: AgentPromptEvalData[];
  }

  let { agentName, agentVersion, agentPromptEvals }: Props = $props();

  // Working mutable state (refreshed on time range changes)
  let evalData = $state<AgentPromptEvalData[]>(agentPromptEvals);
  let isRefreshing = $state(false);
  let lastSeenSignal = $state(timeRangeState.refreshSignal);

  // Viewport-width tracking — mirrors PromptEvalDashboard so chart rebuilds on resize,
  // which also triggers a layout reflow that fixes the table overflow on resize.
  let currentMaxPoints = $state(typeof window !== 'undefined' ? getMaxDataPoints() : 0);

  onMount(() => {
    currentMaxPoints = getMaxDataPoints();
    let timeoutId: ReturnType<typeof setTimeout>;
    const handleResize = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        const newMax = getMaxDataPoints();
        if (newMax !== currentMaxPoints) {
          currentMaxPoints = newMax;
          buildChart();
        }
      }, 400);
    };
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      clearTimeout(timeoutId);
    };
  });

  // ── Time Range Refresh ────────────────────────────────────────────────────────
  // When the time range changes, reset all pagination by calling performRefresh
  // without cursors — this loads fresh data from the beginning for every eval.
  $effect(() => {
    if (isRefreshing) return;
    const newRange = timeRangeState.selectedTimeRange;
    const signal = timeRangeState.refreshSignal;
    const signalFired = signal !== lastSeenSignal;
    if (!newRange) return;

    const rangeChanged = evalData.some(e => {
      if (e.monitoringData.status !== 'success') return false;
      const r = e.monitoringData.selectedTimeRange;
      return r.startTime !== newRange.startTime || r.endTime !== newRange.endTime;
    });

    if (rangeChanged || signalFired) {
      lastSeenSignal = signal;
      evalData.forEach(e => {
        if (e.monitoringData.status === 'success') {
          e.monitoringData.selectedTimeRange = newRange;
        }
      });
      performRefresh();
    }
  });

  /** Full refresh without cursors — resets pagination to page 1. */
  async function performRefresh() {
    isRefreshing = true;
    try {
      await Promise.all(
        evalData.map(async (e) => {
          if (e.monitoringData.status !== 'success') return;
          await refreshGenAIMonitoringData(fetch, e.monitoringData);
        })
      );
    } catch (err) {
      console.error('[AgentEvalDashboard] Refresh failed:', err);
    } finally {
      isRefreshing = false;
    }
  }

  /** Advance the record page for all evals that have a cursor in that direction. */
  async function handleRecordPageChange(direction: string) {
    isRefreshing = true;
    try {
      await Promise.all(
        evalData.map(async (e) => {
          if (e.monitoringData.status !== 'success') return;
          const page = e.monitoringData.selectedData.records;
          const canPage = direction === 'next' ? page?.has_next : page?.has_previous;
          const cursor = direction === 'next' ? page?.next_cursor : page?.previous_cursor;
          if (!canPage || !cursor) return;
          await refreshGenAIMonitoringData(fetch, e.monitoringData, {
            recordCursor: { cursor, direction },
          });
        })
      );
    } catch (err) {
      console.error('[AgentEvalDashboard] Record page change failed:', err);
    } finally {
      isRefreshing = false;
    }
  }

  /** Advance the workflow page for all evals that have a cursor in that direction. */
  async function handleWorkflowPageChange(direction: string) {
    isRefreshing = true;
    try {
      await Promise.all(
        evalData.map(async (e) => {
          if (e.monitoringData.status !== 'success') return;
          const page = e.monitoringData.selectedData.workflows;
          const canPage = direction === 'next' ? page?.has_next : page?.has_previous;
          const cursor = direction === 'next' ? page?.next_cursor : page?.previous_cursor;
          if (!canPage || !cursor) return;
          await refreshGenAIMonitoringData(fetch, e.monitoringData, {
            workflowCursor: { cursor, direction },
          });
        })
      );
    } catch (err) {
      console.error('[AgentEvalDashboard] Workflow page change failed:', err);
    } finally {
      isRefreshing = false;
    }
  }

  // ── Chart ─────────────────────────────────────────────────────────────────────
  Chart.register(zoomPlugin, annotationPlugin, Filler);

  const successEvals = $derived(evalData.filter(e => e.monitoringData.status === 'success'));

  const allWorkflowMetricNames = $derived(
    (() => {
      const names = new Set<string>();
      successEvals.forEach(e => {
        if (e.monitoringData.status !== 'success') return;
        const wf = e.monitoringData.selectedData.metrics?.workflow;
        if (wf?.metrics) Object.keys(wf.metrics).forEach(k => names.add(k));
      });
      return [...names].sort();
    })()
  );

  let selectedMetricName = $state('');

  $effect(() => {
    if (allWorkflowMetricNames.length > 0 && !allWorkflowMetricNames.includes(selectedMetricName)) {
      selectedMetricName = allWorkflowMetricNames[0];
    }
  });

  let chartCanvas = $state<HTMLCanvasElement | null>(null);
  let chart: Chart | null = null;
  let resetZoomTrigger = $state(0);
  let lastResetTrigger = 0;

  $effect(() => {
    if (resetZoomTrigger !== lastResetTrigger && chart) {
      chart.resetZoom();
      lastResetTrigger = resetZoomTrigger;
    }
  });

  function buildChart() {
    if (!chartCanvas || !selectedMetricName) return;

    const evals = successEvals;
    const borderColors = generateColors(evals.length);
    const bgColors = generateColors(evals.length, 0.15);

    const datasets = evals
      .map((e, i) => {
        if (e.monitoringData.status !== 'success') return null;
        const wf = e.monitoringData.selectedData.metrics?.workflow;
        const metricData = wf?.metrics?.[selectedMetricName];
        if (!metricData?.created_at?.length) return null;

        return {
          label: e.promptCard.name,
          data: metricData.created_at.map((ts, idx) => ({
            x: new Date(ts) as any,
            y: metricData.stats[idx]?.avg ?? 0,
          })),
          borderColor: borderColors[i],
          backgroundColor: bgColors[i],
          pointRadius: 4,
          pointHoverRadius: 6,
          fill: false,
          tension: 0.2,
        };
      })
      .filter((d): d is NonNullable<typeof d> => d !== null);

    if (chart) chart.destroy();
    if (datasets.length === 0) { chart = null; return; }

    chart = new Chart(chartCanvas, {
      type: 'line',
      data: { datasets } as any,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true, position: 'bottom' },
          // @ts-ignore
          zoom: {
            pan: { enabled: true, mode: 'xy', modifierKey: 'ctrl' },
            zoom: {
              mode: 'xy',
              drag: {
                enabled: true,
                borderColor: 'rgb(163, 135, 239)',
                borderWidth: 1,
                backgroundColor: 'rgba(163, 135, 239, 0.3)',
              },
            },
          },
          tooltip: {
            cornerRadius: 1,
            backgroundColor: 'rgba(255,255,255,1)',
            borderColor: 'rgb(0,0,0)',
            borderWidth: 1,
            titleColor: 'rgb(0,0,0)',
            bodyColor: 'rgb(0,0,0)',
            titleFont: { size: 13 },
            bodyFont: { size: 12 },
          },
        },
        scales: {
          x: {
            type: 'time',
            border: { display: true, width: 2, color: 'rgb(0,0,0)' },
            time: {
              displayFormats: {
                millisecond: 'HH:mm', second: 'HH:mm', minute: 'HH:mm',
                hour: 'HH:mm', day: 'MM/dd HH:mm',
              },
            },
            grid: { display: true, color: 'rgba(0,0,0,0.1)', tickLength: 8 },
            ticks: { maxTicksLimit: 12, color: 'rgb(0,0,0)', font: { size: 12 } },
          },
          y: {
            title: { display: true, text: selectedMetricName, color: 'rgb(0,0,0)', font: { size: 13 } },
            ticks: { maxTicksLimit: 10, color: 'rgb(0,0,0)', font: { size: 12 } },
            border: { display: true, width: 2, color: 'rgb(0,0,0)' },
            grid: { display: true, color: 'rgba(0,0,0,0.1)', tickLength: 8 },
          },
        },
        layout: { padding: 10 },
      },
    });
  }

  $effect(() => {
    void selectedMetricName;
    void evalData;
    buildChart();
  });

  onDestroy(() => { if (chart) chart.destroy(); });

  // ── Merged Page Data ──────────────────────────────────────────────────────────

  function promptEvalPath(e: AgentPromptEvalData): string {
    return `/opsml/${getRegistryPath(RegistryType.Prompt)}/card/${e.promptCard.space}/${e.promptCard.name}/${e.promptCard.version}/evaluation`;
  }

  /** Merged record page: items from all evals sorted by created_at desc. */
  const recordPage = $derived(
    (() => {
      const items: RecordWithAgent[] = [];
      let hasNext = false;
      let hasPrevious = false;
      evalData.forEach(e => {
        if (e.monitoringData.status !== 'success') return;
        const path = promptEvalPath(e);
        e.monitoringData.selectedData.records?.items?.forEach(r =>
          items.push({ ...r, _agentName: e.promptCard.name, _evalPath: path })
        );
        if (e.monitoringData.selectedData.records?.has_next) hasNext = true;
        if (e.monitoringData.selectedData.records?.has_previous) hasPrevious = true;
      });
      items.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      return { items, hasNext, hasPrevious } satisfies AgentRecordPage;
    })()
  );

  /** Merged workflow page: items from all evals sorted by created_at desc. */
  const workflowPage = $derived(
    (() => {
      const items: WorkflowWithAgent[] = [];
      let hasNext = false;
      let hasPrevious = false;
      evalData.forEach(e => {
        if (e.monitoringData.status !== 'success') return;
        const path = promptEvalPath(e);
        const profile = e.monitoringData.profile as GenAIEvalProfile;
        e.monitoringData.selectedData.workflows?.items?.forEach(w =>
          items.push({ ...w, _agentName: e.promptCard.name, _evalPath: path, _profile: profile })
        );
        if (e.monitoringData.selectedData.workflows?.has_next) hasNext = true;
        if (e.monitoringData.selectedData.workflows?.has_previous) hasPrevious = true;
      });
      items.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      return { items, hasNext, hasPrevious } satisfies AgentWorkflowPage;
    })()
  );
</script>

<div class="mx-auto w-full max-w-full px-4 sm:px-6 lg:px-8 pb-12 space-y-6 overflow-hidden">

  <!-- ── Agent Identity Banner ─────────────────────────────────────────────── -->
  <div class="rounded-base border-2 border-black bg-primary-50 shadow-small p-4 flex items-center gap-3">
    <div class="p-2 bg-primary-500 border-2 border-black rounded-base shadow-small flex-shrink-0">
      <Bot class="w-5 h-5 text-white" />
    </div>
    <div>
      <p class="text-xs font-black uppercase tracking-wider text-primary-700">Agent</p>
      <p class="font-black text-black">
        {agentName}
        <span class="ml-2 badge bg-surface-50 text-primary-800 border border-black text-xs font-bold px-2 py-0.5 rounded-base">
          v{agentVersion}
        </span>
      </p>
    </div>
    <div class="ml-auto flex items-center gap-3">
      {#if isRefreshing}
        <Loader2 class="w-4 h-4 animate-spin text-primary-600" />
      {/if}
      <div class="text-right">
        <p class="text-xs font-black uppercase tracking-wider text-primary-700">Evaluating</p>
        <p class="font-black text-primary-800">
          {agentPromptEvals.length} Prompt{agentPromptEvals.length !== 1 ? 's' : ''}
        </p>
      </div>
    </div>
  </div>

  <!-- ── Overview Stats ───────────────────────────────────────────────────── -->
  <div>
    <p class="text-xs font-black uppercase tracking-wider text-primary-700 mb-3">Overview</p>
    <AgentEvalOverview agentPromptEvals={evalData} />
  </div>

  <!-- ── Workflow Metric Chart ─────────────────────────────────────────────── -->
  <div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden">

    <div class="px-4 py-3 border-b-2 border-black bg-primary-100 flex flex-col sm:flex-row sm:items-center gap-2">
      <div class="flex items-center gap-2 min-w-0">
        <TrendingUp class="w-4 h-4 text-primary-700 flex-shrink-0" />
        <h2 class="font-black text-sm uppercase tracking-wider text-primary-950 truncate">Workflow Metrics</h2>
        <span class="badge rounded-base border border-black bg-surface-50 text-primary-800 text-xs font-bold px-2 py-0.5 flex-shrink-0">
          {successEvals.length} active
        </span>
      </div>

      <div class="flex items-center gap-2 sm:ml-auto overflow-x-auto pb-0.5 min-w-0">
        {#if allWorkflowMetricNames.length > 0}
          <div class="flex items-center gap-2 flex-shrink-0">
            <KeySquare class="w-3.5 h-3.5 text-primary-600 flex-shrink-0" />
            <div class="flex border-2 border-black rounded-base overflow-hidden shadow-small">
              {#each allWorkflowMetricNames as name}
                <button
                  class="px-3 py-1.5 text-xss font-black uppercase tracking-wider border-r border-black last:border-r-0
                         transition-colors duration-100 whitespace-nowrap
                         {selectedMetricName === name
                           ? 'bg-primary-500 text-white'
                           : 'bg-surface-50 text-black hover:bg-primary-100'}"
                  onclick={() => { selectedMetricName = name; }}
                >
                  {name}
                </button>
              {/each}
            </div>
          </div>
        {/if}

        <button
          class="btn rounded-base border-2 border-black bg-surface-50 text-black text-xss font-black
                 uppercase tracking-wider shadow-small shadow-click-small flex-shrink-0
                 transition-transform duration-100 ease-out px-3 py-1.5"
          onclick={() => { resetZoomTrigger++; }}
        >
          Reset Zoom
        </button>
      </div>
    </div>

    <div class="p-4 bg-surface-50 h-[20rem] relative
                {isRefreshing ? 'opacity-60 pointer-events-none' : ''}">
      {#if successEvals.length === 0}
        <div class="flex flex-col items-center justify-center h-full text-primary-700 font-mono text-sm
                    border-2 border-dashed border-black/20 rounded-base">
          <TrendingUp class="w-8 h-8 mb-2 opacity-30" />
          <span>No active evaluations</span>
        </div>
      {:else if allWorkflowMetricNames.length === 0}
        <div class="flex flex-col items-center justify-center h-full text-primary-700 font-mono text-sm
                    border-2 border-dashed border-black/20 rounded-base">
          <KeySquare class="w-8 h-8 mb-2 opacity-30" />
          <span>No workflow metrics available</span>
        </div>
      {:else}
        <canvas bind:this={chartCanvas} class="w-full h-full"></canvas>
      {/if}
    </div>
  </div>

  <!-- ── Evaluation Records Table ──────────────────────────────────────────── -->
  <div class="grid grid-cols-1 gap-6"></div>
  {#if recordPage.items.length > 0 || recordPage.hasPrevious}
    <div class="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl overflow-hidden flex flex-col h-full">
      <div class="bg-primary-100 border-b-2 border-black px-5 py-3 flex items-center justify-between flex-shrink-0">
        <div class="flex items-center gap-2">
          <TableProperties class="w-4 h-4 text-primary-700" />
          <h2 class="font-black text-sm uppercase tracking-wider text-primary-950">Evaluation Records</h2>
        </div>
        <span class="badge rounded-base border border-black bg-surface-50 text-primary-800 text-xs font-bold px-2 py-0.5">
          {recordPage.items.length}
        </span>
      </div>
      <div class="p-2 w-full flex-grow bg-slate-50 min-h-0">
        <AgentEvalRecordTable
          records={recordPage.items}
          hasNext={recordPage.hasNext}
          hasPrevious={recordPage.hasPrevious}
          onPageChange={handleRecordPageChange}
          {isRefreshing}
        />
      </div>
    </div>
  {/if}

 


 

</div>
