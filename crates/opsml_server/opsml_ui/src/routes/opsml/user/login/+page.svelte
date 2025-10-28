
<script lang="ts">
  import { goto } from "$app/navigation";
  import logo from '$lib/images/opsml-logo-small.webp'
  import LoginWarning from "$lib/components/user/LoginWarning.svelte";
  import {  UiPaths, ServerPaths } from "$lib/components/api/routes";
  import { goTop } from "$lib/utils";
  import type { PageProps } from './$types';
  import { type UseLoginSchema } from "$lib/components/user/schema";
  import { uiSettingsStore } from "$lib/components/settings/settings.svelte";
  import { createInternalApiClient } from "$lib/api/internalClient";
  import { userStore } from "$lib/components/user/user.svelte";
  import type { LoginResponse, SsoAuthUrl } from "$lib/components/user/types";
  import { deserialize } from '$app/forms';
  import type { ActionResult } from '@sveltejs/kit';

  let { previousPath }: PageProps = $props();

  let showLoginError: boolean = $state(false);
  let errorMessage: string = $state("Invalid username or password");

  let loginErrors = $state<Partial<Record<keyof UseLoginSchema, string>>>({});


  function parseSuccessResult(data: Record<string, any>) {
      const loginResponse = data as LoginResponse;
      userStore.fromLoginResponse(loginResponse);
      goto(previousPath ?? UiPaths.HOME);
  }

  function parseFailureResult(data: Record<string, any>) {
      showLoginError = true;

      if (data.validationErrors) {
        // @ts-ignore
        loginErrors = data.validationErrors as Partial<Record<keyof UseLoginSchema, string>>;
      } else {
        errorMessage = data.error ?? "Invalid username or password";
      }
      goTop();
  }

  async function handleLogin(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement}) {
    event.preventDefault();
    const data = new FormData(event.currentTarget, event.submitter);

    try {
      // Send login request to server endpoint
      const response = await fetch(event.currentTarget.action, {
        method: 'POST',
        body: data
      });

      const result: ActionResult = deserialize(await response.text());
      
      if (result.type === 'success') {
        // On success, update userStore, redirect to previousPath or home
        parseSuccessResult(result.data as Record<string, any>);
      } else if (result.type === 'failure') {
        parseFailureResult(result.data as Record<string, any>);
      }
    } catch (err) {
      // Handle network or unexpected errors
      showLoginError = true;
      errorMessage = "Login failed. Please try again.";
      console.error("Login error:", err);
      goTop();
    }
  }

  async function redirectToSsoUrl() {

    const resp = await createInternalApiClient(fetch).get(ServerPaths.SSO_AUTH);
    const ssoAuthUrl = (await resp.json() as SsoAuthUrl);

    localStorage.setItem("ssoState", ssoAuthUrl.state);
    localStorage.setItem("ssoCodeVerifier", ssoAuthUrl.code_verifier);

    window.location.href = ssoAuthUrl.url;
  }

</script>

<div class="col-span-12 flex items-center justify-center px-4">
  
<section class="border-gray-100">
  <div class="z-10 mx-auto rounded-2xl bg-surface-50 border-black border-2 shadow p-4 md:w-80 md:px-4">
    <form method="POST" onsubmit={handleLogin}>

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
            name="username"
          />

          {#if loginErrors.username}
            <span class="text-red-500 text-sm">{loginErrors.username}</span>
          {/if}
        </label>


        <label class="text-surface-950 text-sm">Password
          <input
            class="input text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
            type="password" 
            placeholder="Password"
            name="password"
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

        <a class="text-primary-700 hover:text-primary-700" href={UiPaths.RESET}>Forgot password?</a>
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
</div>
