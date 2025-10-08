<script lang="ts">
  import { goto } from "$app/navigation";
  import logo from "$lib/images/opsml-logo-medium.webp";
  import PasswordMessage from "$lib/components/user/PasswordMessage.svelte";
  import { RoutePaths, UiPaths } from "$lib/components/api/routes";
  import { goTop } from "$lib/utils";
  import { opsmlClient } from "$lib/components/api/client.svelte";
  import type { PageProps } from './$types';
  import {  validatePasswordResetSchema, type PasswordResetSchema } from "$lib/components/user/schema";
  import { registerUser, resetUserPassword } from "$lib/components/user/utils";
  import { HelpCircle } from 'lucide-svelte';
  import { userStore } from "$lib/components/user/user.svelte";
  


  let username: string = $state('');
  let recoveryCode: string = $state('');
  let newPassword: string = $state('');
  let confirmPassword: string = $state('');

  let showResetMessage: boolean = $state(false);
  let resetMessage: string = $state("Password reset successful! You can now log in with your new password.");
  let showPasswordHelp: boolean = $state(false);
  let passwordErrors = $state<Partial<Record<keyof PasswordResetSchema, string>>>({});

  async function handleReset() {
    // Handle password reset logic here

    let argsValid = validatePasswordResetSchema(username, recoveryCode, newPassword);

    if (argsValid.success) {
        // assert

        let response = await resetUserPassword(username, recoveryCode, newPassword);

        showResetMessage = true;
        // sleep for 2 seconds to show the message
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        await goto(UiPaths.LOGIN);
        
    } else {
      showPasswordHelp = true;
      passwordErrors = argsValid.errors ?? {};
      goTop();
    }
}


</script>

<section class="pt-20 border-gray-100 col-span-full flex-1 pb-16 md:pb-0 items-center">
  

  <form class="z-10 mx-auto rounded-2xl bg-surface-50 border-black border-2 shadow p-4 md:w-96 md:px-5" onsubmit={handleReset}>

    <img alt="OpsML logo" class="mx-auto -mt-12 mb-3 w-20" src={logo}>
    <h1 class="pt-1 text-center text-lg font-bold text-primary-800">Reset your password</h1>

    {#if showResetMessage}                  
      <PasswordMessage
      message={resetMessage}
      />
    {/if}

    <div class="mb-8 grid grid-cols-1 gap-3">
      <label class="text-surface-950 text-sm">Username
        <input
          class="input text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
          type="text" 
          placeholder="Username"
          bind:value={username}
        />

        {#if passwordErrors.username}
          <span class="text-red-500 text-sm">{passwordErrors.username}</span>
        {/if}
      </label>


      <label class="text-surface-950 relative">
        <div class="flex items-center gap-2 text-sm">
          New Password
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
          placeholder="New Password"
          bind:value={newPassword}
        />

        {#if passwordErrors.newPassword}
          <span class="text-red-500 text-sm">{passwordErrors.newPassword}</span>
        {/if}
      </label>

      <label class="text-surface-950 text-sm">Confirm Password
        <input
          class="input text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
          type="password"
          placeholder="Confirm Password"
          bind:value={confirmPassword}
        />

        {#if passwordErrors.confirmPassword}
          <span class="text-red-500 text-sm">{passwordErrors.confirmPassword}</span>
        {/if}
      </label>


      <label class="text-surface-950 text-sm">Recovery Code
        <input
          class="input text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
          type="text" 
          placeholder="Recovery Code"
          bind:value={recoveryCode}
        />
        {#if passwordErrors.recoveryCode}
          <span class="text-red-500 text-sm">{passwordErrors.recoveryCode}</span>
        {/if}
      </label>
    </div>

    <div class="grid justify-items-center">
      <button type="submit" class="btn text-sm bg-primary-500 rounded-lg md:w-72 justify-self-center text-black mb-2 ring-offset-white  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2 border-black border-2 border-border shadow transition-all hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none">
        Reset
      </button>

    </div>
  </form>
</section>