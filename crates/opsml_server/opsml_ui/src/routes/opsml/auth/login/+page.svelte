
<script lang="ts">
  import { goto, invalidateAll } from "$app/navigation";
  import logo from "$lib/images/opsml-logo.png";
  import LoginWarning from "$lib/components/auth/LoginWarning.svelte";
  import { RoutePaths } from "$lib/components/api/routes";
  import { goTop } from "$lib/utils";
  import { user, authManager } from "$lib/components/auth/AuthStore.svelte";
  import type { PageProps } from './$types';


  let username: string = $state('');
  let password: string = $state('');
  let showLoginError: boolean = $state(false);

 
  let { data }: PageProps = $props();
  let previousPath = data.previousPath;

  async function handleLogin() {
    // Handle login logic here
    let authenticated = await authManager.login(username, password);

    if (authenticated === true) {
      // need to reload the page to update the nav bar
      if (previousPath) {
        goto(previousPath);
      } else {
        goto(RoutePaths.HOME);
      }
    } else {
      showLoginError = true;
      goTop();
    }

  }


</script>

<section class="pt-24 border-gray-100 col-span-full flex-1 pb-16 md:pb-0 items-center">
  {#if showLoginError}
    <LoginWarning
    errorMessage="Invalid username or password"
    />
  {/if}

  <form class="z-10 mx-auto rounded-2xl bg-surface-50 border shadow p-4 md:w-96 md:px-5" onsubmit={handleLogin}>

    <img alt="OpsML logo" class="mx-auto -mt-12 mb-2 w-20" src={logo}>
    <h1 class="pt-1 text-center text-3xl font-bold text-primary-600">Log In</h1>
    <p class="mb-6 text-center text-surface-950">New to OpsML?
      <a class="underline hover:text-primary-700" href={RoutePaths.REGISTER}>Register</a>
    </p>

    <div class="mb-8 grid grid-cols-1 gap-3">
      <label class="text-surface-950">Username
        <input
          class="input rounded-base border-black bg-surface-50 hover:bg-surface-200 text-black disabled:opacity-50"
          type="text" 
          placeholder="Username"
          bind:value={username}
        />
      </label>


      <label class="text-surface-950">Password
        <input
          class="input rounded-base border-black bg-surface-50 hover:bg-surface-200 text-black disabled:opacity-50"
          type="text" 
          placeholder="Password"
          bind:value={password}

        />
      </label>
    </div>

    <div class="grid justify-items-center">
      <button type="submit" class="btn bg-primary-500 rounded-lg md:w-72 justify-self-center text-black mb-2 ring-offset-white  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2 border-black border-2 border-border shadow transition-all hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none">
        Login
      </button>

      <a class="text-primary-700 hover:text-primary-700" href={RoutePaths.FORGOT}>Forgot password?</a>
    </div>
  </form>
</section>