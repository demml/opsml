<script lang="ts">

import Markdown from "$lib/card/Markdown.svelte";
import { goto } from '$app/navigation';

export let hasReadme: boolean;
export let name: string;
export let repository: string;
export let registry: string; 
export let version: string;
export let icon: string;
export let readme: string;

async function createReadme() {
    let baseURL: string = `/opsml/${registry}/card/readme`;

     goto(`${baseURL}?name=${name}&repository=${repository}&version=${version}&status=edit`);
   
  }

</script>

<div class="w-full md:w-3/5 mt-4 ml-4 pl-2 md:ml-12 shadow-md">
  {#if !hasReadme}
      <div class="mt-5 mx-5 py-24 bg-gradient-to-b from-secondary-50 to-white rounded-lg text-center items-center">
        <p class="mb-1 text-lg">No card README found</p>
        <p class="mb-1 text-gray-500">Click button below to create a README!</p>
        <p class="mb-6 text-gray-500">Note: README applies to all versions of a given model and repository </p>
        <button type="button" class="btn variant-filled" on:click={() => createReadme()}>
          <img class="h-5" alt="The project logo" src={icon} />
          <span>Create</span>
        </button>
      </div>
      {:else}
      <div class="mt-2 mr-5">
        <div class="flex rounded-t-lg px-3 min-w-96 justify-end">
          <div>
            <button type="button" class="btn btn-sm bg-primary-500 text-white" on:click={() => { createReadme() }}>
              <span>Edit Readme</span>
            </button>
          </div>
        </div>
        <Markdown 
            source={readme}
            globalPadding='5px'
            globalPaddingMobile='0px'  
        />
      </div>
    {/if}
  </div>