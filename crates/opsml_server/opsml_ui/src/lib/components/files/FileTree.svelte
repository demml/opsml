<script lang="ts">
    // Define the file node structure
    import { type FileNode } from "./types";
    import FileTreeNode from "./FileTreeNode.svelte";

    // Use runes for reactive state
    let { files } = $props<{ files: string[] }>();
    let tree = $state<FileNode[]>([]);
  
    // Convert flat file list into a tree structure
    function buildFileTree(paths: string[]): FileNode[] {
      const root: FileNode[] = [];
      
      paths.forEach(path => {
        const parts = path.split('/');
        let currentLevel = root;
        
        parts.forEach((part, index) => {
          const isLast = index === parts.length - 1;
          const fullPath = parts.slice(0, index + 1).join('/');
          const existing = currentLevel.find(n => n.name === part);
  
          if (!existing) {
            const node: FileNode = {
              name: part,
              type: isLast ? 'file' : 'directory',
              path: fullPath,
              isOpen: false,
              children: isLast ? undefined : []
            };
            currentLevel.push(node);
            if (!isLast) currentLevel = node.children!;
          } else if (!isLast) {
            currentLevel = existing.children!;
          }
        });
      });
  
      return root;
    }
  
    // Update tree whenever files prop changes
    $effect(() => {
      tree = buildFileTree(files);
    });
  </script>
  
  <div class="space-y-1">
    {#each tree as node}
      <FileTreeNode {node} />
    {/each}
  </div>