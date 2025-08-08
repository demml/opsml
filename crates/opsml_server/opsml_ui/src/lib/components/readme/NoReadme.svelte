<script lang="ts">
  import { goto } from '$app/navigation';

let {
      name,
      space,
      version,
      registryPath,
    } = $props<{
      name: string;
      space: string;
      version: string;
      registryPath: string;
    }>();


  function navigateToReadMe() {
      // navigate to readme
      goto(`/opsml/${registryPath}/card/${space}/${name}/${version}/readme`);
    }

</script>

<div class="flex flex-col items-center justify-center h-full gap-4">
  <div class="text-center text-lg font-bold text-black">No ReadMe found</div>
  <div>
    <button 
      class="mb-2 text-black bg-primary-500 text-sm rounded-lg shadow shadow-hover border-black border-2 px-4 w-38 h-10"
      onclick={navigateToReadMe}
    >
      add ReadMe
    </button>
  </div>
</div>
