<script lang="ts">
  import {
    SvelteFlow,
    Controls,
    Background,
    BackgroundVariant,
    //@ts-ignore
  } from '@xyflow/svelte';
  import '@xyflow/svelte/dist/style.css';

  import type { TraceSpan } from '../types';
  import {
    createSpanGraph,
    getPathNodeIds,
    highlightPathNodes,
    highlightPathEdges
  } from './utils';
  import SpanNode from './SpanNode.svelte';
  import { browser } from '$app/environment';

  let {
    spans,
    slowestSpan,
    onSpanSelect,
  }: {
    spans: TraceSpan[];
    slowestSpan?: TraceSpan | null;
    onSpanSelect: (span: TraceSpan) => void;
  } = $props();

  let isDark = $state(browser && document.documentElement.classList.contains('theme-dark'));

  const nodeTypes = {
    span: SpanNode,
  };

  const { nodes: initialNodes, edges: initialEdges, bounds } = $derived(
    createSpanGraph(spans, slowestSpan, isDark)
  );

  let selectedNodeId = $state<string | null>(null);

  const pathNodeIds = $derived(
     // @ts-ignore
    getPathNodeIds(initialNodes, initialEdges, selectedNodeId)
  );

  const nodes = $derived(
    // @ts-ignore
    highlightPathNodes(initialNodes, pathNodeIds, selectedNodeId)
  );

  const edges = $derived(
    highlightPathEdges(initialEdges, pathNodeIds, selectedNodeId)
  );

  const containerHeight = $derived(Math.max(300, Math.min(bounds.height + 100, 600)));

  // Detect dark mode reactively via MutationObserver
  $effect(() => {
    if (!browser) return;
    const observer = new MutationObserver(() => {
      isDark = document.documentElement.classList.contains('theme-dark');
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  });

  function handleNodeClick(event: any) {
    const node = event.detail?.node || event.node;

    if (!node) {
      console.warn('No node found in click event');
      return;
    }

    if (selectedNodeId === node.id) {
      selectedNodeId = null;
    } else {
      selectedNodeId = node.id;
    }

    const nodeData = node.data;
    if (nodeData?.span) {
      onSpanSelect(nodeData.span);
    }
  }

  function handlePaneClick() {
    selectedNodeId = null;
  }
</script>

<div
  class="span-graph-container"
  class:span-graph-dark={isDark}
  style="height: {containerHeight}px;"
  class:has-selection={selectedNodeId !== null}
>
  <SvelteFlow
    nodes={nodes}
    {edges}
    {nodeTypes}
    colorMode={isDark ? 'dark' : 'light'}
    fitView={true}
    fitViewOptions={{
      minZoom: 0.2,
      maxZoom: 1.0,
    }}

    minZoom={0.3}
    maxZoom={1.5}
    defaultEdgeOptions={{
      type: 'smoothstep',
      animated: true,
      markerEnd: {
        type: 'arrowclosed'
      },
    }}
    onnodeclick={handleNodeClick}
    onpaneclick={handlePaneClick}
  >
    <Controls showLock={false} />
    <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
  </SvelteFlow>
</div>

<style>
  /* ─── Container ───────────────────────────────────────────────────────── */
  .span-graph-container {
    width: 100%;
    border: 2px solid black;
    border-radius: var(--border-radius);
    background: var(--color-primary-100);
    overflow: hidden;
  }

  .span-graph-container.span-graph-dark {
    border-color: oklch(35% 0.05 150 / 0.5);
    background: oklch(8% 0.003 150);
  }

  /* ─── Light mode: override --xy-* vars for opsml brutalist style ────── */
  .span-graph-container :global(.svelte-flow) {
    --xy-edge-stroke: black;
    --xy-edge-stroke-width: 1;
    --xy-edge-stroke-selected: black;
    --xy-background-color: transparent;
    --xy-background-pattern-dots-color-default: #91919a;
    --xy-node-background-color: transparent;
    --xy-node-border: none;
    --xy-node-boxshadow-hover: none;
    --xy-node-boxshadow-selected: none;
    --xy-handle-background-color: black;
    --xy-handle-border-color: white;
    --xy-controls-button-background-color: white;
    --xy-controls-button-background-color-hover: var(--color-primary-100);
    --xy-controls-button-color: black;
    --xy-controls-button-border-color: black;
    --xy-controls-box-shadow: var(--shadow-small);
  }

  /* ─── Dark mode: green-hued phosphor terminal look ─────────────────── */
  .span-graph-container.span-graph-dark :global(.svelte-flow) {
    --xy-edge-stroke: oklch(60% 0.10 150);
    --xy-edge-stroke-width: 1;
    --xy-edge-stroke-selected: oklch(72% 0.14 150);
    --xy-background-color: oklch(8% 0.003 150);
    --xy-background-pattern-dots-color-default: oklch(30% 0.04 150 / 0.4);
    --xy-node-background-color: transparent;
    --xy-node-border: none;
    --xy-node-boxshadow-hover: none;
    --xy-node-boxshadow-selected: none;
    --xy-handle-background-color: oklch(60% 0.10 150);
    --xy-handle-border-color: oklch(12% 0.003 150);
    --xy-controls-button-background-color: oklch(12% 0.003 150);
    --xy-controls-button-background-color-hover: oklch(18% 0.004 150);
    --xy-controls-button-color: oklch(60% 0.10 150);
    --xy-controls-button-border-color: oklch(25% 0.01 150 / 0.3);
    --xy-controls-box-shadow: none;
  }

  /* ─── Controls brutalist border override ───────────────────────────── */
  :global(.span-graph-container .svelte-flow__controls) {
    border: 2px solid black;
    border-radius: var(--border-radius);
  }

  .span-graph-dark :global(.svelte-flow__controls) {
    border-color: oklch(35% 0.05 150 / 0.5);
  }

  /* ─── Edge animation (dashed flow) ─────────────────────────────────── */
  :global(.span-graph-container .svelte-flow__edge.animated .svelte-flow__edge-path) {
    stroke-dasharray: 8 4;
    animation: edge-flow 1s linear infinite;
  }

  :global(.span-graph-container .svelte-flow__edge-path) {
    transition: stroke-width 0.2s ease, stroke 0.2s ease;
  }

  /* ─── In-path highlight (selected node ancestry) ───────────────────── */
  :global(.span-graph-container .svelte-flow__edge.in-path .svelte-flow__edge-path) {
    stroke: var(--color-primary-500);
    stroke-width: 3;
    stroke-dasharray: 8 4;
    animation: edge-flow 0.7s linear infinite;
  }

  :global(.span-graph-container .svelte-flow__edge.in-path .svelte-flow__edge-marker),
  :global(.span-graph-container .svelte-flow__edge.in-path .svelte-flow__arrowhead polyline) {
    fill: var(--color-primary-500);
    stroke: var(--color-primary-500);
  }

  .span-graph-dark :global(.svelte-flow__edge.in-path .svelte-flow__edge-path) {
    stroke: oklch(72% 0.14 150);
  }

  .span-graph-dark :global(.svelte-flow__edge.in-path .svelte-flow__edge-marker),
  .span-graph-dark :global(.svelte-flow__edge.in-path .svelte-flow__arrowhead polyline) {
    fill: oklch(72% 0.14 150);
    stroke: oklch(72% 0.14 150);
  }

  /* ─── Error edge styling ───────────────────────────────────────────── */
  :global(.span-graph-container .svelte-flow__edge.error .svelte-flow__edge-path) {
    stroke: var(--color-error-600);
    stroke-width: 2;
  }

  :global(.span-graph-container .svelte-flow__edge.error.in-path .svelte-flow__edge-path) {
    stroke: var(--color-error-600);
    stroke-width: 3;
    animation: edge-flow 0.5s linear infinite;
  }

  :global(.span-graph-container .svelte-flow__edge.error .svelte-flow__edge-marker) {
    fill: var(--color-error-600);
  }

  .span-graph-dark :global(.svelte-flow__edge.error .svelte-flow__edge-path) {
    stroke: oklch(60% 0.15 14);
  }

  .span-graph-dark :global(.svelte-flow__edge.error .svelte-flow__edge-marker) {
    fill: oklch(60% 0.15 14);
  }

  /* ─── Edge hover ───────────────────────────────────────────────────── */
  :global(.span-graph-container .svelte-flow__edge:hover .svelte-flow__edge-path) {
    stroke-width: 3;
  }

  /* ─── Selection dimming ────────────────────────────────────────────── */
  :global(.span-graph-container.has-selection .svelte-flow__node:not(.in-path):not(.selected)) {
    opacity: 0.3;
    transition: opacity 0.2s ease;
  }



  :global(.span-graph-container.has-selection .svelte-flow__edge:not(.in-path)) {
    opacity: 0.3;
    transition: opacity 0.2s ease;
  }

  :global(.span-graph-container.has-selection .svelte-flow__node.in-path),
  :global(.span-graph-container.has-selection .svelte-flow__node.selected) {
    opacity: 1;
    transition: opacity 0.2s ease;
  }

  :global(.span-graph-container.has-selection .svelte-flow__edge.in-path) {
    opacity: 1;
    transition: opacity 0.2s ease;
  }

  @keyframes edge-flow {
    to {
      stroke-dashoffset: -12;
    }
  }
</style>
