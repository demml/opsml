<script lang="ts">

  import { type ModelMetadata } from "$lib/scripts/types";
  import Fa from 'svelte-fa'
  import { faTag, faIdCard, faFolderOpen } from '@fortawesome/free-solid-svg-icons'
  import icon from '$lib/images/opsml-green.ico'

	/** @type {import('./$types').LayoutData} */
	export let data;

  let hasReadme: boolean;
  $: hasReadme = data.hasReadme;

  let metadata: ModelMetadata;
  $: metadata = data.metadata;

</script>

<div class="flex flex-wrap">
  <div class="w-full md:w-3/5 border-r border-grey-100 pl-4 md:pl-20">
    {#if !hasReadme}
      <div class="mt-5 mr-5 py-24 bg-gradient-to-b from-secondary-50 to-white rounded-lg text-center items-center">
        <p class="mb-1">No card README found</p>
        <p class="mb-1 text-sm text-gray-500">Click button below to create a README!</p>
        <p class="mb-6 text-sm text-gray-500">Note: README applies to all versions of a given model and repository </p>
        <button type="button" class="btn variant-filled">
          <img class="h-5" alt="The project logo" src={icon} />
          <span>Create</span>
        </button>
      </div>
      {:else}
        <div id="editor" class="h-96"></div>
    {/if}
  </div>
  <div class="w-full md:w-1/3 mt-5 pl-4">
    <div class="pl-4">
      <header class="mb-2 text-lg font-bold">Metadata</header>

      <!-- UID -->
      <div class="flex flex-row gap-1 items-center">
        <div class="w-8">
          <Fa class="h-12" icon={faIdCard} color="#04cd9b"/>
        </div>
        <div class="w-32 font-semibold text-gray-500">ID:</div>
        <div class="w-48 ">0uyoiulkjhoiuho</div>
      </div>

      <!-- name -->
      <div class="flex flex-row gap-1 items-center">
        <div class="w-8">
          <Fa class="h-12" icon={faIdCard} color="#04cd9b"/>
        </div>
        <div class="w-32 font-semibold text-gray-500">Name:</div>
        <div class="w-48 ">{metadata.model_name}</div>
      </div>

      <!-- version -->
      <div class="flex flex-row gap-1 items-center">
        <div class="w-8">
          <Fa class="h-12" icon={faIdCard} color="#04cd9b"/>
        </div>
        <div class="w-32 font-semibold text-gray-500">Version:</div>
        <div class="w-48 ">{metadata.model_version}</div>
      </div>

      <!-- repository -->
      <div class="flex flex-row gap-1 items-center">
        <div class="w-8">
          <Fa class="h-12" icon={faFolderOpen} color="#04cd9b"/>
        </div>
        <div class="w-32 font-semibold text-gray-500">Respository:</div>
        <div class="w-48 ">{metadata.model_repository}</div>
      </div>
    </div>
  </div>
</div>