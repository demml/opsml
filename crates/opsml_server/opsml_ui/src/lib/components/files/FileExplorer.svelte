<script lang="ts">
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import type { RegistryType } from '$lib/utils';
  import type { FileTreeNode, RawFile } from './types';
  import FileTree from './FileTree.svelte';
  import FileViewPage from './FileViewPage.svelte';

  interface Props {
    initialTree: FileTreeNode[];
    rawFile: RawFile | null;
    viewPath: string | null;
    basePath: string;
    uid: string;
    registryType: RegistryType;
    space: string;
    name: string;
    version: string;
  }

  let {
    initialTree,
    rawFile,
    viewPath,
    basePath,
    uid,
    registryType,
    space,
    name,
    version,
  }: Props = $props();

  // Tree endpoint is always at <current-files-page>/tree — works for both agent and non-agent routes
  const treePath = $derived(page.url.pathname.replace(/\/$/, '') + '/tree');

  let expandedDirs: Set<string> = $state(new Set());
  let loadingDirs: Set<string> = $state(new Set());
  let dirCache: Map<string, FileTreeNode[]> = $state(new Map());

  async function handleFolderToggle(node: FileTreeNode) {
    if (expandedDirs.has(node.path)) {
      const next = new Set(expandedDirs);
      next.delete(node.path);
      expandedDirs = next;
      return;
    }

    if (!dirCache.has(node.path)) {
      const nextLoading = new Set(loadingDirs);
      nextLoading.add(node.path);
      loadingDirs = nextLoading;

      try {
        const treeUrl = `${treePath}?path=${encodeURIComponent(node.path)}`;
        const res = await fetch(treeUrl);
        const treeData = await res.json();
        const nextCache = new Map(dirCache);
        nextCache.set(node.path, treeData.files);
        dirCache = nextCache;
      } finally {
        const nextLoading = new Set(loadingDirs);
        nextLoading.delete(node.path);
        loadingDirs = nextLoading;
      }
    }

    const nextExpanded = new Set(expandedDirs);
    nextExpanded.add(node.path);
    expandedDirs = nextExpanded;
  }

  function handleFileSelect(node: FileTreeNode) {
    goto(`?view=${encodeURIComponent(node.path)}`, { replaceState: false });
  }

  function handleClose() {
    goto('?', { replaceState: false });
  }

  const splitPath = $derived(viewPath ? viewPath.split('/') : []);
</script>

{#if viewPath}
  <!-- Mobile: full-width viewer with back button -->
  <div class="lg:hidden w-full pb-2 pt-2">
    <div class="flex items-center mb-3">
      <button
        class="btn text-sm bg-surface-50 text-primary-800 border-2 border-black shadow-small shadow-click-small rounded-base font-bold flex items-center gap-1"
        onclick={handleClose}
      >
        ← Back to Files
      </button>
    </div>
    {#if rawFile}
      <FileViewPage
        file={rawFile}
        splitPath={splitPath}
        registry={registryType}
        {space}
        {name}
        {version}
        disableNavigation={true}
        onClose={handleClose}
      />
    {/if}
  </div>

  <!-- Desktop: split panel — full viewport height, both sides independently scrollable -->
  <div class="hidden lg:grid gap-4 w-full h-[calc(100vh-120px)]" style="grid-template-columns: min(320px, 32%) 1fr">
    <!-- Left: file tree — independently scrollable, stays in place -->
    <div class="overflow-y-auto h-full pb-2 pr-2 pt-4">
      <FileTree
        nodes={initialTree}
        {basePath}
        depth={0}
        {expandedDirs}
        {loadingDirs}
        {dirCache}
        selectedPath={viewPath}
        compact={true}
        onFolderToggle={handleFolderToggle}
        onFileSelect={handleFileSelect}
      />
    </div>

    <!-- Right: file viewer — independently scrollable -->
    <div class="overflow-y-auto h-full min-w-0 pr-8 pt-3">
      {#if rawFile}
        <FileViewPage
          file={rawFile}
          splitPath={splitPath}
          registry={registryType}
          {space}
          {name}
          {version}
          disableNavigation={true}
          onClose={handleClose}
        />
      {/if}
    </div>
  </div>
{:else}
  <!-- No file selected: tree takes full width on all breakpoints -->
  <div class="max-w-6xl pb-2 pr-1 pt-4 mx-auto">
    <FileTree
      nodes={initialTree}
      {basePath}
      depth={0}
      {expandedDirs}
      {loadingDirs}
      {dirCache}
      selectedPath={null}
      onFolderToggle={handleFolderToggle}
      onFileSelect={handleFileSelect}
    />
  </div>
{/if}
