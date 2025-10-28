<script lang="ts">
  import { goto } from "$app/navigation";
  import logo from "$lib/images/opsml-logo-medium.webp";
  import PasswordMessage from "$lib/components/user/PasswordMessage.svelte";
  import { ServerPaths, UiPaths } from "$lib/components/api/routes";
  import { goTop } from "$lib/utils";
  import { type PasswordResetSchema } from "$lib/components/user/schema";
  import { HelpCircle, Eye, EyeOff } from 'lucide-svelte';
  import { deserialize } from '$app/forms';
  import type { ActionResult } from '@sveltejs/kit';
  

  let showResetMessage: boolean = $state(false);
  let resetMessage: string = $state("Password reset successful! You can now log in with your new password.");
  let showPasswordHelp: boolean = $state(false);
  let passwordErrors = $state<Partial<Record<keyof PasswordResetSchema, string>>>({});
  let passwordVisible: boolean = $state(false);
  let isSubmitting: boolean = $state(false);

  function togglePasswordHelp() {
    showPasswordHelp = !showPasswordHelp;
  }

  function togglePasswordVisibility() {
    passwordVisible = !passwordVisible;

  }

  function parseSuccessResult(data: Record<string, any>) {
    showResetMessage = true;
    resetMessage = "Password reset successful! You can now log in with your new password.";
    goto(UiPaths.LOGIN);
  }

  function parseFailureResult(data: Record<string, any>) {
    showResetMessage = true;
    
    if (data.validationErrors) {
      resetMessage = "Please correct the errors below.";
      passwordErrors = data.validationErrors as Partial<Record<keyof PasswordResetSchema, string>>;
    } else {
      resetMessage = data.error ?? "Password reset failed. Please try again.";
      passwordErrors = {}; // Clear validation errors for general errors
    }
    goTop();
  }

  /**
 * Handles password reset form submission.
 * Validates input, sends reset request, and manages UI feedback.
 * @param event Form submit event
 */
async function handleReset(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement}) {
  event.preventDefault();

  showResetMessage = false;
  passwordErrors = {};
  isSubmitting = true;

  try {
      const data = new FormData(event.currentTarget, event.submitter);

      const response = await fetch(event.currentTarget.action, {
        method: 'POST',
        body: data
      });

      const result: ActionResult = deserialize(await response.text());

      if (result.type === 'success') {
        parseSuccessResult(result.data as Record<string, any>);
      } else if (result.type === 'failure') {
        parseFailureResult(result.data as Record<string, any>);
      }

    } catch (error) {
      showResetMessage = true;
      resetMessage = "Error. Please try again later.";
      passwordErrors = {};
      goTop();
    } finally {
      isSubmitting = false;
    }
  }

</script>

<section class="col-span-12 flex items-center justify-center px-4">
  <form class="z-10 mx-auto rounded-2xl bg-surface-50 border-black border-2 shadow p-4 md:w-96 md:px-5" onsubmit={handleReset}>
    <!-- Logo and Header -->
    <img alt="OpsML logo" class="mx-auto -mt-12 mb-3 w-20" src={logo}>
    <h1 class="pt-1 mb-4 text-center text-lg font-bold text-primary-800">Reset your password</h1>

    <!-- Reset Message -->
    {#if showResetMessage}                  
      <div class="mb-4">
        <PasswordMessage message={resetMessage} />
      </div>
    {/if}

    <!-- Form Fields -->
    <div class="mb-6 space-y-4">
      <!-- Username Field -->
      <div class="space-y-1">
        <div class="text-surface-950 text-sm">Username</div>
        <input
          class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
          type="text" 
          placeholder="Username"
          name="username"
        />
        {#if passwordErrors.username}
          <span class="text-red-500 text-sm">{passwordErrors.username}</span>
        {/if}
      </div>

      <!-- New Password Field -->
      <div class="space-y-1">
        <div class="flex items-center justify-between relative">
          <div class="flex items-center gap-1">
            <span class="text-surface-950 text-sm">New Password</span>
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
            name="newPassword"
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
        {#if passwordErrors.newPassword}
          <span class="text-red-500 text-sm">{passwordErrors.newPassword}</span>
        {/if}
      </div>

      <!-- Confirm Password Field -->
      <div class="space-y-1">
        <div class="text-surface-950 text-sm">Confirm Password</div>
        <div class="relative">
          <input
            class="input w-full text-sm pr-10 rounded-base bg-surface-50 text-black focus-visible:ring-2 focus-visible:ring-primary-800"
            type={passwordVisible ? 'text' : 'password'}
            name="confirmPassword"
            placeholder="Confirm Password"
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
        {#if passwordErrors.confirmPassword}
          <span class="text-red-500 text-sm">{passwordErrors.confirmPassword}</span>
        {/if}
      </div>

      <!-- Recovery Code Field -->
      <div class="space-y-1">
        <div class="text-surface-950 text-sm">Recovery Code</div>
        <input
          class="input w-full text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
          type="text" 
          placeholder="Recovery Code"
          name="recoveryCode"
        />
        {#if passwordErrors.recoveryCode}
          <span class="text-red-500 text-sm">{passwordErrors.recoveryCode}</span>
        {/if}
      </div>
    </div>

    <!-- Submit Button -->
    <div class="flex justify-center">
      <button 
        type="submit" 
        disabled={isSubmitting}
        class="btn w-full md:w-72 text-sm bg-primary-500 rounded-lg text-black ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2 border-black border-2 shadow transition-all hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none"
      >
        {isSubmitting ? 'Resetting...' : 'Reset'}
      </button>
    </div>
  </form>
</section>