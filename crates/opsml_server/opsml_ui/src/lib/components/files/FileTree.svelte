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
  

<div class="rounded-lg border-2 border-black shadow bg-slate-100 overflow-auto">
  <table class="table-auto w-full text-black overflow-hidden text-sm bg-slate-100">
    <thead class="bg-primary-500">
      <tr>
        <th class="text-black pl-4 py-2 text-left">Name</th>
        <th class="text-black p-2 text-left">Size</th>
        <th class="text-black pr-4 py-2 text-right">Created</th>
      </tr>
    </thead>
    <tbody>
      {#if !isRoot}
        <tr class="border-t hover:bg-primary-300 py-2">
          <td class="pl-4 py-2">
            <button class="btn flex flex-row gap-2 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg" onclick={() => goto(previousPath)}>
              <Folder />
              <div class="text-black">..</div>
            </button>
          </td>
          <td class="p-2">
            <span></span>
          </td>
          <td class="pr-4 py-2 text-black text-right"></td>
        </tr>
      {/if}
      {#each files as file}
      <tr class="border-t hover:bg-primary-300 py-2 bg-white">
        <td class="pl-4 py-2">
          {#if file.object_type === 'directory'}
            <button class="btn text-sm flex flex-row gap-2 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg" onclick={() => navigateToPath(file.name)}>
                <Folder />
              <div class="text-black">{file.name}</div>
            </button>
            {:else if file.size < 50 * 1024 * 1024 && isAcceptableSuffix(file.suffix)}
              <button class="btn text-sm flex flex-row gap-2 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg" onclick={() => navigateToView(file.path)}>
                  <File />
                  <div class="text-black">{file.name}</div>
              </button>
            {:else}
              <div class="flex flex-row gap-2">
                  <File />
                  <div class="text-black">{file.name}</div>
              </div>
            {/if}
        </td>
        <td class="p-2">
          {#if file.object_type === 'directory'}
            <span></span>
          {:else}
            <div class="text-black">{formatBytes(file.size)}</div>
          {/if}
        </td>
        <td class="pr-4 py-2 text-black text-right">{timeAgo(file.created_at)}</td>
      </tr>
      {/each}
    </tbody>
  </table>
</div>  