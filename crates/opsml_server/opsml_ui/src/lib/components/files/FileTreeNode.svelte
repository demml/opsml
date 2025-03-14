<script lang="ts">
    import { type FileNode } from "./types";
    import Self from "./FileTreeNode.svelte";

    let { node } = $props<{ node: FileNode }>();
    let isOpen = $state(false);
  
    function toggleDirectory() {
      isOpen = !isOpen;
    }
  </script>
  
  <div class="flex flex-col">
    <button
      class="flex items-center gap-2 px-2 py-1 hover:bg-gray-100 rounded-md"
      onclick={toggleDirectory}
    >
      {#if node.type === 'directory'}
        <span>{isOpen ? '📂' : '📁'}</span>
      {:else}
        <span>📄</span>
      {/if}
      <span>{node.name}</span>
    </button>
  
    {#if node.type === 'directory' && isOpen}
      <div class="ml-4">
        {#each node.children || [] as childNode}
          <Self node={childNode} />
        {/each}
      </div>
    {/if}
  </div>