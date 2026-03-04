<script lang="ts">
  import type { FileTreeNode } from './types';
  import { Folder, FolderOpen, File, ChevronRight, ChevronDown, Loader } from 'lucide-svelte';
  import { formatBytes, timeAgo, isAcceptableSuffix } from './utils';
  import FileTree from './FileTree.svelte';

  interface Props {
    nodes: FileTreeNode[];
    basePath: string;
    depth?: number;
    expandedDirs: Set<string>;
    loadingDirs: Set<string>;
    dirCache: Map<string, FileTreeNode[]>;
    selectedPath: string | null;
    onFolderToggle: (node: FileTreeNode) => void;
    onFileSelect: (node: FileTreeNode) => void;
  }

  let {
    nodes,
    basePath,
    depth = 0,
    expandedDirs,
    loadingDirs,
    dirCache,
    selectedPath,
    onFolderToggle,
    onFileSelect,
  }: Props = $props();
</script>

<div class="{depth === 0 ? 'rounded-base border-2 border-black shadow bg-surface-50 overflow-hidden' : ''}">
  {#if depth === 0}
    <div class="flex items-center px-3 py-1.5 border-b-2 border-black bg-surface-200 sticky top-0 z-5">
      <span class="flex-1 text-xs font-black uppercase tracking-wider text-primary-700 pl-10">Name</span>
      <span class="text-xs font-black uppercase tracking-wider text-primary-700 w-20 text-right">Size</span>
      <span class="text-xs font-black uppercase tracking-wider text-primary-700 w-24 text-right ml-2">Modified</span>
    </div>
  {/if}
  {#each nodes as node}
    {@const isExpanded = expandedDirs.has(node.path)}
    {@const isLoading = loadingDirs.has(node.path)}
    {@const isSelected = selectedPath === node.path}
    {@const children = dirCache.get(node.path) ?? []}

    <div>
      <div
        class="flex items-center gap-2 py-2 pr-3 border-b border-black/10 transition-colors duration-100 {isSelected ? 'bg-primary-100' : 'hover:bg-primary-50 bg-surface-50'}"
        style="padding-left: {8 + depth * 16}px"
      >
        {#if node.object_type === 'directory'}
          <button
            class="flex items-center gap-2 flex-1 text-left min-w-0"
            onclick={() => onFolderToggle(node)}
          >
            {#if isLoading}
              <Loader class="w-4 h-4 animate-spin text-primary-500 shrink-0" />
            {:else if isExpanded}
              <ChevronDown class="w-4 h-4 text-primary-700 shrink-0" />
            {:else}
              <ChevronRight class="w-4 h-4 text-primary-700 shrink-0" />
            {/if}
            {#if isExpanded}
              <FolderOpen class="w-4 h-4 text-primary-600 shrink-0" />
            {:else}
              <Folder class="w-4 h-4 text-primary-600 shrink-0" />
            {/if}
            <span class="text-sm font-medium text-black truncate">{node.name}</span>
          </button>
          <span class="text-xs font-mono text-primary-700 shrink-0 w-20 text-right"></span>
          <span class="text-xs text-primary-700 font-mono shrink-0 w-24 text-right ml-2">{timeAgo(node.created_at)}</span>

        {:else if node.size < 50 * 1024 * 1024 && isAcceptableSuffix(node.suffix)}
          <button
            class="flex items-center gap-2 flex-1 text-left min-w-0"
            onclick={() => onFileSelect(node)}
          >
            <span class="w-4 shrink-0"></span>
            <File class="w-4 h-4 text-primary-600 shrink-0" />
            <span class="text-sm truncate {isSelected ? 'font-bold text-primary-900' : 'text-black'}">{node.name}</span>
          </button>
          <span class="text-xs font-mono text-primary-700 shrink-0 w-20 text-right">{formatBytes(node.size)}</span>
          <span class="text-xs text-primary-700 font-mono shrink-0 w-24 text-right ml-2">{timeAgo(node.created_at)}</span>

        {:else}
          <div class="flex items-center gap-2 flex-1 min-w-0">
            <span class="w-4 shrink-0"></span>
            <File class="w-4 h-4 text-primary-400 shrink-0" />
            <span class="text-sm text-primary-500 truncate">{node.name}</span>
          </div>
          <span class="text-xs font-mono text-primary-700 shrink-0 w-20 text-right">{formatBytes(node.size)}</span>
          <span class="text-xs text-primary-700 font-mono shrink-0 w-24 text-right ml-2">{timeAgo(node.created_at)}</span>
        {/if}
      </div>

      {#if node.object_type === 'directory' && isExpanded}
        {#if isLoading}
          <div class="py-2 text-xs text-primary-600 italic" style="padding-left: {24 + depth * 16}px">
            Loading...
          </div>
        {:else if children.length > 0}
          <FileTree
            nodes={children}
            {basePath}
            depth={depth + 1}
            {expandedDirs}
            {loadingDirs}
            {dirCache}
            {selectedPath}
            {onFolderToggle}
            {onFileSelect}
          />
        {:else}
          <div class="py-2 text-xs text-primary-500 italic" style="padding-left: {24 + depth * 16}px">
            Empty directory
          </div>
        {/if}
      {/if}
    </div>
  {/each}
</div>
