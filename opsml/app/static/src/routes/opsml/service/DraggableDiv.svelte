<script lang="ts">
    export let id: string;
    export let content: string;
  
    function handleDragStart(event: DragEvent) {
      if (event.dataTransfer) {
        event.dataTransfer.setData('text/plain', id);
        event.dataTransfer.effectAllowed = 'move';
      }
    }
  </script>
  
  <div draggable="true" on:dragstart={handleDragStart} class="draggable">
    {content}
  </div>
  
  <style>
    .draggable {
      padding: 10px;
      background-color: #f0f0f0;
      border: 1px solid #ccc;
      cursor: move;
      margin-bottom: 5px;
    }
  </style>