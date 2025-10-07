<script lang="ts">
  import type { PageProps } from './$types';
  import logo from "$lib/images/opsml-logo-medium.webp";
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { UiPaths } from "$lib/components/api/routes";
  import { go } from "svelte-highlight/languages";
  import type { LoginResponse } from '$lib/components/user/types';


  let { data }: PageProps = $props();
  let response = data.response as LoginResponse;

   onMount(async () => {

      // Check if the user is authenticated
      if (!response.authenticated) {
        setTimeout(() => {
          goto(UiPaths.LOGIN);
        }, 3000);
      }

      goto(UiPaths.HOME);
   });

</script>

<div class="pt-24 border-gray-100 col-span-full flex-1 pb-16 md:pb-0 items-center">
  

  <div class="z-10 mx-auto rounded-2xl bg-surface-50 border-black border-2 shadow p-4 md:w-md md:px-5">

    <img alt="OpsML logo" class="mx-auto -mt-12 mb-3 w-20" src={logo}>
    <h1 class="pt-1 text-center text-3xl font-bold text-primary-800">Success!</h1>

    <div class="mb-8 grid grid-cols-1 gap-3">
      <div>
        <p class="text-left text-primary-500">You have successfully logged in!</p>
      </div>

      <p class="text-center text-black">You will now be redirected.</p>

    </div>

  </div>
</div>