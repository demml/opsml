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
  import { max } from 'date-fns';

  let {
    spans,
    slowestSpan,
    onSpanSelect,
  }: {
    spans: TraceSpan[];
    slowestSpan?: TraceSpan | null;
    onSpanSelect: (span: TraceSpan) => void;
  } = $props();

  const nodeTypes = {
    span: SpanNode,
  };

  const { nodes: initialNodes, edges: initialEdges, bounds } = $derived(
    createSpanGraph(spans, slowestSpan)
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
  style="height: {containerHeight}px;"
  class:has-selection={selectedNodeId !== null}
>
  <SvelteFlow
    nodes={nodes}
    {edges}
    {nodeTypes}
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
      style: 'stroke: #000; stroke-width: 2;',
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
  .span-graph-container {
    width: 100%;
    border: 2px solid black;
    border-radius: var(--border-radius);
    background: var(--color-primary-100);
    overflow: hidden;
  }

  :global(.span-graph-container .svelte-flow__background) {
    background-color: var(--color-surface-500);
  }

  :global(.span-graph-container .svelte-flow__controls) {
    background: white;
    border: 2px solid black;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-small);
  }

  :global(.span-graph-container .svelte-flow__controls-button) {
    background: white;
    border: none;
    border-bottom: 1px solid black;
    padding: 8px;
    width: 100%;
    transition: all 0.2s ease;
  }

  :global(.span-graph-container .svelte-flow__controls-button:last-child) {
    border-bottom: none;
  }

  :global(.span-graph-container .svelte-flow__controls-button:hover) {
    background: var(--color-primary-100);
  }

  :global(.span-graph-container .svelte-flow__controls-button svg) {
    fill: black;
  }

  /* Edge styling */
  :global(.span-graph-container .svelte-flow__edge-path) {
    stroke: black;
    stroke-width: 2;
    transition: stroke-width 0.2s ease, stroke 0.2s ease;
  }

  :global(.span-graph-container .svelte-flow__edge.animated .svelte-flow__edge-path) {
    stroke-dasharray: 8 4;
    animation: edge-flow 1s linear infinite;
  }

  :global(.span-graph-container .svelte-flow__edge.in-path .svelte-flow__edge-path) {
    stroke: var(--color-primary-500);
    stroke-width: 3;
    stroke-dasharray: 8 4;
    animation: edge-flow 0.7s linear infinite;
  }

  :global(.span-graph-container .svelte-flow__edge.error .svelte-flow__edge-path) {
    stroke: var(--color-error-600);
    stroke-width: 2;
  }

  :global(.span-graph-container .svelte-flow__edge.error.in-path .svelte-flow__edge-path) {
    stroke: var(--color-error-600);
    stroke-width: 3;
    animation: edge-flow 0.5s linear infinite;
  }

  :global(.span-graph-container .svelte-flow__edge .svelte-flow__edge-marker) {
    fill: black;
    transition: fill 0.2s ease;
  }

  :global(.span-graph-container .svelte-flow__edge.in-path .svelte-flow__edge-marker) {
    fill: var(--color-primary-500);
  }

  :global(.span-graph-container .svelte-flow__edge.error .svelte-flow__edge-marker) {
    fill: var(--color-error-600);
  }

  @keyframes edge-flow {
    to {
      stroke-dashoffset: -12;
    }
  }

  :global(.span-graph-container .svelte-flow__edge:hover .svelte-flow__edge-path) {
    stroke-width: 3;
  }

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



</style>