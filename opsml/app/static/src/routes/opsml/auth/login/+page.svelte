
<script lang="ts">
  import { goto } from "$app/navigation";
  import logo from "$lib/images/opsml-logo.png";
  import { authStore, login } from "$lib/scripts/auth/newAuthStore";
  import LoginWarning from "$lib/components/LoginWarning.svelte";
  import { CommonPaths } from "$lib/scripts/types";
  import { goTop } from "$lib/scripts/utils";
  import { onMount } from "svelte";
  import { get } from "svelte/store";
  import OktaLogin from "$lib/components/auth/OktaLogin.svelte";

  let username = '';
  let password = '';

  let showLoginError: boolean = false;
  let authType: string = '';

  onMount(() => {
    // check if user is already logged in
    const auth = get(authStore);
    authType = auth.authType;

    if (auth.isAuthenticated) {
      goto(CommonPaths.HOME);
    }
    
  });

  /** @type {import('./$types').PageData} */
  export let data;
  let previousPath = data.previousPath;

  async function handleLogin() {
    // Handle login logic here
    
    await login(username, password);
    const auth = get(authStore);

    if (auth.isAuthenticated) {
      // need to reload the page to update the nav bar
      if (previousPath) {
        goto(previousPath);
      } else {
        goto(CommonPaths.HOME);
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

    <form class="z-10 mx-auto rounded-2xl bg-slate-100 border shadow p-4 md:w-96 md:px-5" on:submit|preventDefault={handleLogin}>

      <img alt="OpsML logo" class="mx-auto -mt-12 mb-2 w-20" src={logo}>
      <h1 class="pt-1 text-center text-3xl font-bold text-primary-500">Log In</h1>
      <p class="mb-6 text-center text-gray-500">New to OpsML?
        <a class="underline hover:text-primary-700" href={CommonPaths.REGISTER}>Register</a>
      </p>

      <div class="mb-8 grid grid-cols-1 gap-3">
        <label class="text-primary-500">Username
          <input
            class="input rounded-lg bg-slate-200 hover:bg-slate-100"
            type="text" 
            placeholder="Username"
            bind:value={username}
          />
        </label>

        <label class="text-primary-500">Password
          <input
            class="input rounded-lg bg-slate-200 hover:bg-slate-100"
            type="text" 
            placeholder="Password"
            bind:value={password}

          />
        </label>
      </div>

      {#if authType === 'okta'}
      <OktaLogin />
      {/if}

      <div class="grid justify-items-center">
        <button type="submit" class="btn bg-primary-500 text-white rounded-lg md:w-72 justify-self-center mb-2">
          <span>Login</span>
        </button>
        <a class="text-primary-500 hover:text-primary-700" href={CommonPaths.FORGOT}>Forgot password?</a>
      </div>
    </form>
  </section>
