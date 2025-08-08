<script lang="ts">
  import { type RegistryType, getRegistryTypeLowerCase } from "$lib/utils";

 
  let { 
     key, 
     value,
     registryType,
   } = $props<{
      key: string;
      value: string;
      registryType: RegistryType;
   }>();

</script>

<div class="inline-flex items-stretch overflow-hidden rounded-lg border-2 border-primary-700 w-fit shadow-primary-small shadow-hover-small h-7 text-sm">
  <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic flex items-center justify-center">{key}</div> 
    <div class="px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950 flex items-center justify-center">
      <a 
        href="/opsml/{getRegistryTypeLowerCase(registryType)}/{value}" 
        class="text-primary-900"
        data-sveltekit-preload-data="hover"
        >
        Link
      </a>
    </div>
</div>