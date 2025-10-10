<script lang="ts">
  import { goto } from "$app/navigation";
  import logo from "$lib/images/opsml-logo-medium.webp";
  import {  ServerPaths, UiPaths } from "$lib/components/api/routes";
  import { serverClient } from "$lib/api/svelteServerClient";
  import { userStore } from "$lib/components/user/user.svelte";
  import Warning from "$lib/components/utils/Warning.svelte";
  import type { LogOutResponse } from "$lib/components/user/types";

  let showLogoutError: boolean = $state(false);
  let errorMessage: string = $state("Failed to logout");

  async function handleLogout() {
    let res = await serverClient.get(ServerPaths.LOGOUT);
    let loggedOut = (await res.json() as LogOutResponse);

    if (loggedOut) {
      // update the user store
      userStore.resetUser();
      // redirect to login page
      await goto(UiPaths.LOGIN);
    } else {
      showLogoutError = true;
    }
  }

</script>

<div class="col-span-12 flex items-center justify-center px-4">
  <section class="pt-4 border-gray-100 col-span-full flex-1 pb-16 md:pb-0 items-center">
    <form class="z-10 mx-auto rounded-2xl bg-surface-50 border-black border-2 shadow p-4 md:w-96 md:px-5" onsubmit={handleLogout}>

      <img alt="OpsML logo" class="mx-auto -mt-12 mb-2 w-20" src={logo}>
      <h1 class="pt-1 text-center text-lg font-bold text-primary-800">Logout</h1>

      <p class="mb-6 text-center text-surface-950 text-smd">
        You are about to logout. Click the logout button below to proceed.
      </p>

      {#if showLogoutError}
        <Warning {errorMessage} />
      {/if}
  
      <div class="grid justify-items-center">
        <button type="submit" class="btn text-smd bg-primary-500 rounded-lg md:w-72 justify-self-center text-black mb-2 ring-offset-white  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2 border-black border-2 border-border shadow transition-all hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none">
          Logout
        </button>

      </div>
    </form>
  </section>
</div>