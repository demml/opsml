<script lang="ts">

  import { goto } from '$app/navigation';
  import { UiPaths } from '$lib/components/api/routes';
  import logo from '$lib/images/opsml-logo-medium.webp';
  import type { PageProps } from './$types';

  let { data }: PageProps = $props();
  let message = data.message;

  function navigateToHome() {
    goto(UiPaths.HOME);
  }

</script>



<div class="col-span-12 md:col-start-5 md:col-span-4 flex items-center justify-center px-4">

  <div class="rounded-2xl bg-surface-50 border-black border-2 shadow p-4 w-sm md:w-xl lg:w-2xl md:px-5">
    
    <img alt="OpsML logo" class="mx-auto -mt-12 mb-2 w-20" src={logo}>
    <h1 class="pt-1 text-center text-lg font-bold text-error-500">Oops!</h1>
    <p class="mb-6 text-center text-black">The page encountered an error</p>

    <div class="mb-8 grid grid-cols-1 gap-3">
      <h2 class="text-primary-800 font-bold">Error</h2>
      <p class="mb-1 text-black text-center overflow-x-scroll text-sm">{message}</p>
    </div>

    <div class="grid justify-items-center">
      <button type="submit" class="btn text-sm bg-primary-500 rounded-lg md:w-72 justify-self-center text-black mb-2 ring-offset-white  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2 border-black border-2 border-border shadow transition-all hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none" onclick={navigateToHome}>
        <span>Return to Homepage</span>
      </button>
    </div>

  </div>
</div>
