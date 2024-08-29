<script lang="ts">
    import { Handle, Position, type NodeProps } from '@xyflow/svelte';
    import type { Writable } from 'svelte/store';
   
    type $$Props = NodeProps;

    export let data: { package_name: Writable<string>, version: Writable<string> };
   
    const { package_name } = data;
    const { version } = data;

  </script>
   
  <div class="package">
    <div class="border border-darkpurple shadow-md rounded-md bg-primary-50">
      <Handle type="target" position={Position.Top} />
      <div class="flex flex-col">
        <div class="flex flex-row">
          <div class="px-2 rounded-l-md text-darkpurple bg-primary-50 italic">{$package_name}</div> 
          <div class="px-2 border-l border-darkpurple rounded-r-md text-darkpurple bg-surface-50">{$version}</div>
        </div>
      </div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  </div>

  
  <style>
    :global(.svelte-flow__node-selectorNode) {
      font-size: 8px;
      border: 1px solid #555;
      border-radius: 5px;
      text-align: center;
    }
  </style>