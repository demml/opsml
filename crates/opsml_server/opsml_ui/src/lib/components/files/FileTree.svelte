<script lang="ts">
    // Define the file node structure
    
  import { type FileTreeNode } from "./types";
  import { Folder, File } from 'lucide-svelte';
  import { formatBytes, timeAgo } from "./utils";
  import { goto } from "$app/navigation";
  import { isAcceptableSuffix } from "./utils";
  import { getRegistryPath, type RegistryType } from "$lib/utils";
  // Use runes for reactive state
  let { files, 
        currentPath, 
        previousPath, 
        space, 
        name, 
        version, 
        isRoot ,
        registryType
      } = $props<{ 
        files: FileTreeNode[], 
        currentPath:string, 
        previousPath: string, 
        space:string, 
        name:string, 
        version: string, 
        isRoot: boolean ,
        registryType: RegistryType
      }>();



  function navigateToPath(slug_name: string) {
    let newPath = currentPath + '/' + slug_name;
    goto(newPath);
  }

  function navigateToView(path: string) {
    // add params to path
    let viewPath = `/opsml/${getRegistryPath(registryType)}/card/${space}/${name}/${version}/files/view?path=${path}`;
    goto(viewPath);
  }
   
  </script>
  

<div class="rounded-base border-2 border-black shadow bg-surface-50 overflow-auto">
  <table class="table-auto w-full text-black overflow-hidden text-sm">
    <thead class="bg-primary-500 border-b-2 border-black">
      <tr>
        <th class="pl-4 py-2 text-left">
          <span class="px-2 py-1 rounded bg-white text-primary-800 text-xs font-bold uppercase tracking-wide border border-black shadow-small">Name</span>
        </th>
        <th class="p-2 text-left">
          <span class="px-2 py-1 rounded bg-white text-primary-800 text-xs font-bold uppercase tracking-wide border border-black shadow-small">Size</span>
        </th>
        <th class="pr-4 py-2 text-right">
          <span class="px-2 py-1 rounded bg-white text-primary-800 text-xs font-bold uppercase tracking-wide border border-black shadow-small">Created</span>
        </th>
      </tr>
    </thead>
    <tbody>
      {#if !isRoot}
        <tr class="border-t border-black/10 hover:bg-primary-50 transition-colors duration-100">
          <td class="pl-4 py-2">
            <button class="btn flex flex-row gap-2 items-center bg-primary-500 text-white border-2 border-black shadow-small shadow-click-small rounded-base text-sm font-bold" onclick={() => goto(previousPath)}>
              <Folder class="w-4 h-4" />
              <span>..</span>
            </button>
          </td>
          <td class="p-2"></td>
          <td class="pr-4 py-2 text-right"></td>
        </tr>
      {/if}
      {#each files as file}
      <tr class="border-t border-black/10 hover:bg-primary-50 transition-colors duration-100 bg-surface-50">
        <td class="pl-4 py-2">
          {#if file.object_type === 'directory'}
            <button class="btn text-sm flex flex-row gap-2 items-center bg-primary-500 text-white border-2 border-black shadow-small shadow-hover-small rounded-base font-bold" onclick={() => navigateToPath(file.name)}>
              <Folder class="w-4 h-4" />
              <span>{file.name}</span>
            </button>
          {:else if file.size < 50 * 1024 * 1024 && isAcceptableSuffix(file.suffix)}
            <button class="btn text-sm flex flex-row gap-2 items-center bg-surface-50 text-primary-800 border-2 border-black shadow-small shadow-hover-small rounded-base font-medium" onclick={() => navigateToView(file.path)}>
              <File class="w-4 h-4" />
              <span>{file.name}</span>
            </button>
          {:else}
            <div class="flex flex-row gap-2 items-center pl-1 text-primary-800">
              <File class="w-4 h-4" />
              <span>{file.name}</span>
            </div>
          {/if}
        </td>
        <td class="p-2">
          {#if file.object_type !== 'directory'}
            <span class="font-mono text-sm text-primary-700">{formatBytes(file.size)}</span>
          {/if}
        </td>
        <td class="pr-4 py-2 text-primary-700 text-right font-mono text-sm">{timeAgo(file.created_at)}</td>
      </tr>
      {/each}
    </tbody>
  </table>
</div>