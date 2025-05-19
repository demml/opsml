<script lang="ts">
  import { goto } from "$app/navigation";
  import logo from "$lib/images/opsml-logo.png";
  import { UiPaths } from "$lib/components/api/routes";
  import { userStore } from "$lib/components/user/user.svelte";
  

  async function gotoLogin() {
    goto(UiPaths.LOGIN);
  }


</script>

<div class="pt-24 border-gray-100 col-span-full flex-1 pb-16 md:pb-0 items-center">
  

  <div class="z-10 mx-auto rounded-2xl bg-surface-50 border-black border-2 shadow p-4 md:w-96 md:px-5">

    <img alt="OpsML logo" class="mx-auto -mt-12 mb-3 w-20" src={logo}>
    <h1 class="pt-1 text-center text-3xl font-bold text-primary-800">Welcome to OpsML!</h1>

    <div class="mb-8 grid grid-cols-1 gap-3">
      <div>
        <p class="text-center">You have successfully registered as a new user! Below you will find your recovery codes:</p>
        <p class="text-center">Please save these codes in a safe place, as they are required for account recovery.</p>
        <ul class="list-disc ml-4 mt-1">
          {#each userStore.recovery_codes as code}
            <li>{code}</li>
          {/each}
        </ul>
      </div>

      <p class="text-center">When you are ready, click the button below to navigate back to the login screen</p>

    </div>

    <div class="grid justify-items-center">
      <button type="submit" class="btn bg-primary-500 rounded-lg md:w-72 justify-self-center text-black mb-2 ring-offset-white  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2 border-black border-2 border-border shadow transition-all hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none" onclick={gotoLogin}>
        Login
      </button>

    </div>
  </div>
</div>