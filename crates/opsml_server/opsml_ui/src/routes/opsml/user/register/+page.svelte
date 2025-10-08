<script lang="ts">
  import { goto } from "$app/navigation";
  import logo from "$lib/images/opsml-logo-medium.webp";
  import LoginWarning from "$lib/components/user/LoginWarning.svelte";
  import { RoutePaths, UiPaths } from "$lib/components/api/routes";
  import { goTop } from "$lib/utils";
  import { opsmlClient } from "$lib/components/api/client.svelte";
  import type { PageProps } from './$types';
  import {  validateUserRegisterSchema, type UserRegisterSchema } from "$lib/components/user/schema";
  import { registerUser } from "$lib/components/user/utils";
  import { HelpCircle, Eye, EyeOff } from 'lucide-svelte';
  import { userStore } from "$lib/components/user/user.svelte";
  


  let username: string = $state('');
  let password: string = $state('');
  let email: string = $state('');
  let reEnterPassword: string = $state('');
  let showLoginError: boolean = $state(false);
  let errorMessage: string = $state("Error encountered during registration");
  let showPasswordHelp: boolean = $state(false);
  let passwordVisible: boolean = $state(false);

  let registerErrors = $state<Partial<Record<keyof UserRegisterSchema, string>>>({});

  function togglePasswordHelp() {
    showPasswordHelp = !showPasswordHelp;
  }

  function togglePasswordVisibility() {
    passwordVisible = !passwordVisible;

  }

  async function handleRegister() {
    // Handle registration logic here

    let argsValid = validateUserRegisterSchema(username, password, reEnterPassword, email);

    if (argsValid.success) {
        let response = await registerUser(username, password, email);

      if (response.registered) {
        // need to goto the register success page to give user recovery codes
        userStore.setRecoveryCodes(response.response?.recovery_codes ?? []);
        goto(UiPaths.REGISTER_SUCCESS);

      } else {
        showLoginError = true;
        console.error("Registration error:", response.error);
        errorMessage = response.error ?? "Error encountered during registration";
      }
      goTop();


    } else {
      showLoginError = true;
      errorMessage = "Please correct the errors below.";
      console.error("Validation errors:", argsValid.errors);
      registerErrors = argsValid.errors ?? {};
      goTop();
    }
}


</script>

<div class="flex col-span-full items-center justify-center pb-16 md:pb-0">

<section class="border-gray-100">

  <form class="z-10 mx-auto rounded-2xl bg-surface-50 border-black border-2 shadow p-4 md:w-96 md:px-5 min-h-fit" onsubmit={handleRegister}>

    <img alt="OpsML logo" class="mx-auto -mt-12 mb-3 w-20" src={logo}>
    <h1 class="pt-1 text-center text-lg font-bold text-primary-800">Register a new profile</h1>

    {#if showLoginError}
      <LoginWarning
      errorMessage={errorMessage}
      />
    {/if}

    <div class="mb-8 grid grid-cols-1 gap-3">
      <!-- Username Field -->
      <div class="space-y-1">
        <div class="text-surface-950 text-smd">Username</div>
        <input
          class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
          type="text" 
          placeholder="Username"
          bind:value={username}
        />
        {#if registerErrors.username}
          <span class="text-red-500 text-sm">{registerErrors.username}</span>
        {/if}
      </div>

      <div class="space-y-1">
        <div class="flex items-center justify-between relative">
          <div class="flex items-center gap-1">
            <span class="text-surface-950 text-smd">Password</span>
            <button
              type="button"
              class="text-surface-600 hover:text-surface-900"
              onclick={togglePasswordHelp}
            >
              <HelpCircle size={16} />
            </button>
          </div>
          {#if showPasswordHelp}
            <div class="absolute z-50 top-8 left-0 p-2 bg-surface-100 border border-surface-300 rounded-md shadow-lg text-sm w-64 text-surface-900">
              Password must:
              <ul class="list-disc ml-4 mt-1">
                <li>Be 8-32 characters long</li>
                <li>Include at least one uppercase letter</li>
                <li>Include at least one number</li>
                <li>Include at least one special character</li>
              </ul>
            </div>
          {/if}
        </div>

        <div class="relative">
          <input
            class="input w-full text-sm pr-10 rounded-base bg-surface-50 text-black focus-visible:ring-2 focus-visible:ring-primary-800"
            type={passwordVisible ? 'text' : 'password'}
            bind:value={password}
            placeholder="Password"
          />
          <button
            type="button"
            class="absolute inset-y-0 right-0 flex items-center px-2 text-surface-600"
            onclick={togglePasswordVisibility}
          >
            {#if passwordVisible}
              <Eye size={16} color="#5948a3"/>
            {:else}
              <EyeOff size={16} color="#5948a3" />
            {/if}
          </button>
        </div>
        {#if registerErrors.password}
          <span class="text-red-500 text-sm">{registerErrors.password}</span>
        {/if}
      </div>
      <!-- Re-enter Password Field -->
      <div class="space-y-1">
        <div class="text-surface-950 text-smd">Re-enter Password</div>
        <div class="relative">
          <input
            class="input w-full text-sm pr-10 rounded-base bg-surface-50 text-black focus-visible:ring-2 focus-visible:ring-primary-800"
            type={passwordVisible ? 'text' : 'password'}
            bind:value={reEnterPassword}
            placeholder="Re-enter Password"
          />
          <button
            type="button"
            class="absolute inset-y-0 right-0 flex items-center px-2 text-surface-600"
            onclick={togglePasswordVisibility}
          >
            {#if passwordVisible}
              <Eye size={16} color="#5948a3"/>
            {:else}
              <EyeOff size={16} color="#5948a3" />
            {/if}
          </button>
        </div>
        {#if registerErrors.reEnterPassword}
          <span class="text-red-500 text-sm">{registerErrors.reEnterPassword}</span>
        {/if}
      </div>
      <!-- Email Field -->
      <div class="space-y-1">
        <div class="text-surface-950 text-smd">Email (leave blank if username is email)</div>
        <input
          class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
          type="email" 
          placeholder="Email"
          bind:value={email}
        />
        {#if registerErrors.email}
          <span class="text-red-500 text-sm">{registerErrors.email}</span>
        {/if}
      </div>
    </div>

    <div class="grid justify-items-center mt-4">
      <button type="submit" class="btn text-smd bg-primary-500 rounded-lg md:w-72 justify-self-center text-black mb-2 ring-offset-white  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2 border-black border-2 border-border shadow transition-all hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none">
        Register
      </button>

    </div>
  </form>
</section>
</div>