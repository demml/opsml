
<script lang="ts">
  import { goto } from "$app/navigation";
  import logo from "$lib/images/opsml-logo.png";
  import LoginWarning from "$lib/components/user/LoginWarning.svelte";
  import {  UiPaths } from "$lib/components/api/routes";
  import { goTop } from "$lib/utils";
  import { userStore } from "$lib/components/user/user.svelte";
  import type { PageProps } from './$types';
  import { validateLoginSchema, type UseLoginSchema } from "$lib/components/user/schema";
  import { getSsoAuthURL } from "$lib/components/user/utils";
import { uiSettingsStore } from "$lib/components/settings/settings.svelte";

  let username: string = $state('');
  let password: string = $state('');
  let showLoginError: boolean = $state(false);
  let errorMessage: string = $state("Invalid username or password");

  let loginErrors = $state<Partial<Record<keyof UseLoginSchema, string>>>({});

 
  let { data }: PageProps = $props();
  let previousPath = data.previousPath;

  async function handleLogin() {
    // Handle login logic here

    let argsValid = validateLoginSchema(username, password);

    if (argsValid.success) {
  
      let loginResponse = await userStore.login(username, password);

      if (loginResponse.authenticated === true) {
        // need to reload the page to update the nav bar
        if (previousPath) {
          goto(previousPath);
        } else {
          goto(UiPaths.HOME);
        }
      } else {
        showLoginError = true;
        errorMessage = loginResponse.message;
      }
      goTop();
    } else {
      showLoginError = true;
      loginErrors = argsValid.errors ?? {};
      goTop();
    }
}

async function redirectToSsoUrl() {
  
  const ssoAuthUrl = await getSsoAuthURL();
  localStorage.setItem("ssoState", ssoAuthUrl.state);
  localStorage.setItem("ssoCodeVerifier", ssoAuthUrl.code_verifier);

  window.location.href = ssoAuthUrl.url;
}

</script>

<section class="pt-24 border-gray-100 col-span-full flex-1 pb-16 md:pb-0 items-center">
  

  <div class="z-10 mx-auto rounded-2xl bg-surface-50 border-black border-2 shadow p-4 md:w-80 md:px-4">
    <form onsubmit={handleLogin}>

      <img alt="OpsML logo" class="mx-auto -mt-12 mb-2 w-20" src={logo}>
      <h1 class="pt-1 text-center text-lg font-bold text-primary-800">Log In</h1>
      <p class="mb-4 text-center text-surface-950 text-sm">New to OpsML?
        <a class="underline hover:text-primary-700" href={UiPaths.REGISTER}>Register</a>
      </p>

      {#if showLoginError}
        <LoginWarning
        errorMessage={errorMessage}
        />
      {/if}

      <div class="mb-4 grid grid-cols-1 gap-3">
        <label class="text-surface-950 text-sm">Username
          <input
            class="input text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
            type="text" 
            placeholder="Username"
            bind:value={username}
          />

          {#if loginErrors.username}
            <span class="text-red-500 text-sm">{loginErrors.username}</span>
          {/if}
        </label>


        <label class="text-surface-950 text-sm">Password
          <input
            class="input text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
            type="text" 
            placeholder="Password"
            bind:value={password}
          />
          {#if loginErrors.password}
            <span class="text-red-500 text-sm">{loginErrors.password}</span>
          {/if}
        </label>
      </div>

      <div class="grid justify-items-center">
        <button type="submit" class="btn text-sm bg-primary-500 rounded-lg md:w-64 justify-self-center text-black mb-2 ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2 border-black border-2 border-border shadow transition-all hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none">
          Login
        </button>

        <a class="text-primary-700 hover:text-primary-700" href={UiPaths.FORGOT}>Forgot password?</a>
      </div>
    </form>

    {#if uiSettingsStore.ssoEnabled}
      <div class="grid justify-items-center gap-1">
        <span class="px-4 text-surface-950 bg-surface-50">or</span>
        <button class="btn text-sm bg-secondary-500 rounded-lg md:w-64 justify-self-center text-black mb-2 ring-offset-white  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2 border-black border-2 border-border shadow transition-all hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none" onclick={redirectToSsoUrl}>
          Login with SSO
        </button>
      </div>
    {/if}
   
  </div>

</section>

