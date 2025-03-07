<script lang="ts">

  import { goto } from '$app/navigation';
  import { RoutePaths } from '$lib/components/api/routes';
  import logo from '$lib/images/opsml-logo.png';
  import type { PageProps } from './$types';

  let { data }: PageProps = $props();
  let message = data.message;

  function navigateToHome() {
    goto(RoutePaths.HOME);
  }

</script>



<div class="min-h-screen flex items-center justify-center md:grid md:space-y-0 w-full h-full md:grid-cols-12 md:flex-1 md:grid-rows-full space-y-4 md:gap-6 max-w-full max-h-full bg-gradient-to-b from-surface-300 via-primary-100 via-70% to-primary-100">
  <section class="pt-24 border-gray-100 col-span-full flex-1 pb-16 items-center">

    <div class="z-10 mx-auto rounded-2xl bg-surface-50 border shadow p-4 md:w-96 md:px-5">

      <img alt="OpsML logo" class="mx-auto -mt-12 mb-2 w-20" src={logo}>
      <h1 class="pt-1 text-center text-3xl font-bold text-error-500">Oops!</h1>
      <p class="mb-6 text-center text-black">The page encountered an error</p>

      <div class="mb-8 grid grid-cols-1 gap-3">
        <h2 class="text-primary-800 font-bold">Error</h2>
        <p class="mb-1 text-black text-center">{message}</p>

      </div>

      <div class="grid justify-items-center">
        <button type="submit" class="btn bg-primary-500 rounded-lg md:w-72 justify-self-center text-black mb-2 ring-offset-white  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2 border-black border-2 border-border shadow transition-all hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none" onclick={navigateToHome}>
          <span>Return to Homepage</span>
        </button>
      </div>
      
    </div>
  </section>
</div>