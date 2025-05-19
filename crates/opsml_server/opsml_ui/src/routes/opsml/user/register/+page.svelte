<script lang="ts">
  import { goto } from "$app/navigation";
  import logo from "$lib/images/opsml-logo.png";
  import LoginWarning from "$lib/components/user/LoginWarning.svelte";
  import { RoutePaths, UiPaths } from "$lib/components/api/routes";
  import { goTop } from "$lib/utils";
  import { opsmlClient } from "$lib/components/api/client.svelte";
  import type { PageProps } from './$types';
  import {  validateUserRegisterSchema, type UserRegisterSchema } from "$lib/components/user/schema";
  import { registerUser } from "$lib/components/user/utils";
  import { type CreateUserUiResponse } from "$lib/components/user/types";
  import { HelpCircle } from 'lucide-svelte';
  


  let username: string = $state('');
  let password: string = $state('');
  let email: string = $state('');
  let showLoginError: boolean = $state(false);
  let errorMessage: string = $state("Error encountered during registration");
  let showPasswordHelp: boolean = $state(false);

  let registerErrors = $state<Partial<Record<keyof UserRegisterSchema, string>>>({});

  async function handleRegister() {
    // Handle registration logic here

    let argsValid = validateUserRegisterSchema(username, password, email);

    if (argsValid.success) {
        let response = await registerUser(username, password, email);

      if (response.registered) {
        // need to reload the page to update the nav bar
        goto(UiPaths.HOME);

      } else {
        showLoginError = true;
        errorMessage = response.error ?? "Error encountered during registration";
      }
      goTop();


    } else {
      showLoginError = true;
      registerErrors = argsValid.errors ?? {};
      goTop();
    }
}


</script>

<section class="pt-24 border-gray-100 col-span-full flex-1 pb-16 md:pb-0 items-center">
  

  <form class="z-10 mx-auto rounded-2xl bg-surface-50 border-black border-2 shadow p-4 md:w-96 md:px-5" onsubmit={handleRegister}>

    <img alt="OpsML logo" class="mx-auto -mt-12 mb-3 w-20" src={logo}>
    <h1 class="pt-1 text-center text-3xl font-bold text-primary-800">Register a new profile</h1>

    {#if showLoginError}
      <LoginWarning
      errorMessage={errorMessage}
      />
    {/if}

    <div class="mb-8 grid grid-cols-1 gap-3">
      <label class="text-surface-950">Username
        <input
          class="input text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
          type="text" 
          placeholder="Username"
          bind:value={username}
        />

        {#if registerErrors.username}
          <span class="text-red-500 text-sm">{registerErrors.username}</span>
        {/if}
      </label>


      <label class="text-surface-950 relative">
        <div class="flex items-center gap-2">
          Password
          <button
            type="button"
            class="text-surface-600 hover:text-surface-900"
            onmouseenter={() => showPasswordHelp = true}
            onmouseleave={() => showPasswordHelp = false}
            onfocus={() => showPasswordHelp = true}
            onblur={() => showPasswordHelp = false}
          >
            <HelpCircle size={16} />
          </button>
        </div>
        
        {#if showPasswordHelp}
          <div class="absolute z-50 mt-1 p-2 bg-surface-100 border border-surface-300 rounded-md shadow-lg text-sm w-64">
            Password must:
            <ul class="list-disc ml-4 mt-1">
              <li>Be 8-32 characters long</li>
              <li>Include at least one uppercase letter</li>
              <li>Include at least one number</li>
              <li>Include at least one special character</li>
            </ul>
          </div>
        {/if}

        <input
          class="input text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
          type="password"
          placeholder="Password"
          bind:value={password}
        />
        
        {#if registerErrors.password}
          <span class="text-red-500 text-sm">{registerErrors.password}</span>
        {/if}
      </label>


      <label class="text-surface-950">Email (leave blank if username is email)
        <input
          class="input text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
          type="text" 
          placeholder="Email"
          bind:value={email}
        />
        {#if registerErrors.email}
          <span class="text-red-500 text-sm">{registerErrors.email}</span>
        {/if}
      </label>
    </div>

    <div class="grid justify-items-center">
      <button type="submit" class="btn bg-primary-500 rounded-lg md:w-72 justify-self-center text-black mb-2 ring-offset-white  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2 border-black border-2 border-border shadow transition-all hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none">
        Register
      </button>

    </div>
  </form>
</section>