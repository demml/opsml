<script lang="ts">
  //@ts-ignore
  import { Handle, Position, type NodeProps } from '@xyflow/svelte';
  import { AlertCircle, Clock } from 'lucide-svelte';
  import type { TraceSpan } from '../types';

  interface SpanNodeData {
    span: TraceSpan;
    serviceName: string;
    hasError: boolean;
    duration: string;
    isSlowest: boolean;
    isInPath: boolean;
    isSelected: boolean;
  }

  type Props = NodeProps & { data: SpanNodeData };

  let { data }: Props = $props();
  const { span, serviceName, hasError, duration, isSlowest, isInPath, isSelected } = data;

  const nodeClasses = $derived(() => {
    let classes = 'span-node p-2 border-2';

    if (isSelected) {
      classes += ' border-secondary-500 bg-secondary-100 is-selected';
    } else if (hasError) {
      classes += ' border-error-800 bg-error-100';
    } else if (isSlowest) {
      classes += ' border-retro-orange-900 bg-retro-orange-100';
    } else {
      classes += ' border-primary-800 bg-surface-100';
    }

    if (isInPath && !isSelected) {
      classes += ' is-in-path';
    }

    return classes;
  });

  function getServiceBadgeClasses() {
    if (hasError) return 'border-error-800 bg-surface-50 text-error-800';
    if (isSlowest) return 'border-retro-orange-900 bg-surface-50 text-retro-orange-900';
    if (span.depth === 0) return 'border-tertiary-950 bg-tertiary-100 text-tertiary-950';
    return 'border-primary-800 bg-surface-50 text-primary-900';
  }
</script>

<div class={nodeClasses()}>
  <Handle type="target" position={Position.Left} class="span-handle" />

  <div class="span-node-content">
    <!-- Service Badge -->
    <div class="flex items-center gap-1 mb-1">
      <span class="service-badge {getServiceBadgeClasses()} text-xs p-1 border-1 rounded">
        {serviceName}
      </span>

      {#if hasError}
        <AlertCircle class="w-3 h-3 text-error-600" />
      {/if}

      {#if isSlowest}
        <Clock class="w-3 h-3 text-retro-orange-900" />
      {/if}
    </div>

    <div class="span-name" title={span.span_name}>
      {span.span_name}
    </div>

    <div class="span-duration font-mono text-sm text-gray-700">
      {duration}
    </div>

    {#if span.depth > 0}
      <div class="depth-badge {isSlowest ? 'bg-retro-orange-900' : hasError ? 'bg-error-600' : 'bg-primary-800'}">
        L{span.depth}
      </div>
    {/if}
  </div>

  <Handle type="source" position={Position.Right} class="span-handle" />
</div>

<style>
  .span-node {
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-small);
    min-width: 10rem;
    position: relative;
    transition: all 0.2s ease;
  }

  .span-node:hover {
    transform: translate(2px, 2px);
    box-shadow: none;
  }

  .span-node.is-in-path {
    box-shadow: 0 0 0 3px var(--color-primary-500);
  }

  .span-node.is-selected {
    box-shadow: 0 0 0 4px var(--color-primary-500);
    transform: scale(1.05);
  }

  .span-node-content {
    display: flex;
    flex-direction: column;
  }

  .span-name {
    font-weight: 700;
    color: #000;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 140px;
  }

  .depth-badge {
    position: absolute;
    top: 3px;
    right: 3px;
    color: white;
    font-size: 8px;
    padding: 2px 4px;
    border-radius: 3px;
    border: 1px solid black;
    font-weight: bold;
  }

  :global(.span-handle) {
    width: 8px;
    height: 8px;
    background: black;
    border: 2px solid white;
    border-radius: 50%;
  }

  :global(.span-handle:hover) {
    background: var(--color-primary-500);
  }
</style>