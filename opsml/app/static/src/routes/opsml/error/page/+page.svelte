<script lang="ts">

  import { goto } from '$app/navigation';
  import { CommonPaths } from '$lib/scripts/types';
  import logo from '$lib/images/opsml-logo.png';

  /** @type {import('./$types').PageData} */
	export let data;

  export let message: string;
  message = data.message;

  function navigateToHome() {
    goto(CommonPaths.HOME);
  }

</script>



<div class="flex min-h-screen min-h-screen flex flex-col md:grid md:space-y-0 w-full h-full md:grid-cols-12 md:flex-1 md:grid-rows-full space-y-4 md:gap-6 max-w-full max-h-full bg-gradient-to-b from-surface-500 via-secondary-200 via-70% to-white">
  <section class="pt-24 border-gray-100 col-span-full flex-1 pb-16 items-center">

    <div class="z-10 mx-auto rounded-2xl bg-slate-100 border shadow p-4 md:w-96 md:px-5">

      <img alt="OpsML logo" class="mx-auto -mt-12 mb-2 w-20" src={logo}>
      <h1 class="pt-1 text-center text-3xl font-bold text-error-500">Oops!</h1>
      <p class="mb-6 text-center text-gray-500">The page encountered an error</p>

      <div class="mb-8 grid grid-cols-1 gap-3">
        <h2 class="text-primary-500 font-bold">Error</h2>
        <p class="mb-1 text-primary-500 text-center">{message}</p>

      </div>

      <div class="grid justify-items-center">
        <button type="submit" class="btn bg-primary-500 text-white rounded-lg md:w-72 justify-self-center mb-2" on:click={navigateToHome}>
          <span>Return to Homepage</span>
        </button>
      </div>
      
    </div>
  </section>
</div>