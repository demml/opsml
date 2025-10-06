
<script lang="ts">
  import { resolveCardPathFromArgs } from "./utils";
  import type { QueryPageResponse} from "$lib/components/card/types";
  import  { RegistryType } from "$lib/utils";
  import { goto } from "$app/navigation";
  
  let { registryPage, registry } = $props<{
    registryPage: QueryPageResponse;
    registry: RegistryType;
  }>();


</script>

<div class="pt-4">
  <div class="overflow-auto w-full border-2 border-black rounded-lg">
    <table class="text-black border-collapse text-sm bg-white w-full">
      <thead class="sticky top-0 z-10 bg-white" style="box-shadow: 0 2px 0 0 #000;">
        <tr>
          <th class="p-2 font-heading pl-6 text-left text-black">
            <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
              Space
            </span>
          </th>
          <th class="p-2 font-heading">
            <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
              Name
            </span>
          </th>
          <th class="p-2 font-heading">
            <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
              Last Updated
            </span>
          </th>
          <th class="p-2 font-heading">
            <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
              Current Version
            </span>
          </th>
          <th class="p-2 font-heading">
            <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
              Versions
            </span>
          </th>
          <th class="p-2 font-heading">
            <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
              Link
            </span>
          </th>
        </tr>
      </thead>
      <tbody>
      {#each registryPage.summaries as summary, i}
        <tr class={`border-b-2 border-black hover:bg-primary-300 ${i % 2 === 0 ? 'bg-white' : 'bg-white'}`}>
          <td class="p-1 pl-8">{summary.space}</td>
          <td class="p-1 text-center">{summary.name}</td>
          <td class="p-1 text-center ">
            <div class="badge bg-secondary-100 text-black items-center gap-1 px-2 py-1">
              {summary.updated_at}
            </div>
          </td>
          <td class="p-1 text-center">
            <div class="badge bg-error-100 text-black items-center gap-1 px-2 py-1">
              {summary.version}
            </div>
          </td>
          <td class="p-1 text-center">{summary.versions}</td>
          <td class="p-2">
            <a 
              class="justify-self-center btn text-sm flex flex-row gap-1 bg-primary-500 shadow shadow-hover border-black border-2 rounded-lg"
              href={resolveCardPathFromArgs(registry, summary.space, summary.name, summary.version)}
              data-sveltekit-preload-data="hover"
              >
              <div class="text-black">Link</div>
            </a>
          </td>
        </tr>
      {/each}
      </tbody>
    </table>
  </div>
</div>
