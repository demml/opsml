<script lang="ts">
    import type { DraggableItem } from './types';
    
    export let items: DraggableItem[] = [];
    export let containerId: string;
  
    function handleDragOver(event: DragEvent) {
      event.preventDefault();
      if (event.dataTransfer) {
        event.dataTransfer.dropEffect = 'move';
      }
    }
  
    function handleDrop(event: DragEvent) {
      event.preventDefault();
      const itemId = event.dataTransfer?.getData('text/plain');
      if (itemId) {
        // Dispatch an event to handle the item movement in the parent component
        dispatch('itemDropped', { itemId, targetContainerId: containerId });
      }
    }
  </script>
  
  <div 
    class="container" 
    on:dragover={handleDragOver} 
    on:drop={handleDrop}
  >
    <slot></slot>
    {#each items as item (item.id)}
      <svelte:component this={item.component} id={item.id} content={item.content} />
    {/each}
  </div>
  
  <style>
    .container {
      border: 2px dashed #ccc;
      padding: 10px;
      min-height: 100px;
    }
  </style>