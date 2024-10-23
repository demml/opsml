
<script lang="ts">
  import { goto } from "$app/navigation";
  import logo from "$lib/images/opsml-logo.png";
  import { authManager } from "$lib/scripts/auth/authManager";
  import { getSecurity, getToken, resetPassword,type SecurityReturn, type TokenReturn, type PasswordReturn } from "$lib/scripts/auth/utils";
  import LoginWarning from "$lib/components/LoginWarning.svelte";
  import { CommonPaths, type PasswordStrength } from "$lib/scripts/types";
  import { goTop} from "$lib/scripts/utils";
  import { checkPasswordStrength, delay } from "$lib/scripts/utils";
  import { ProgressBar } from '@skeletonlabs/skeleton';
  import { getToastStore, type ToastSettings } from '@skeletonlabs/skeleton';
  import { sleep } from "$lib/scripts/utils";

  // toast
  const toastStore = getToastStore();
  const t: ToastSettings = {
      message: 'Password updated. Redirecting to login page...',
    };

  let warnUser: boolean = false;
  let errorMessage: string = '';
  let passStrength = 0;
  let passMessage: string | undefined;

  /** @type {import('./$types').PageData} */
  export let data;
  let username: string | undefined = data.username;
  let secretQuestion: string = '';
  let secretAnswer = '';
  let showReset: boolean = false;
  let newPassword = '';

  let checkPassword = delay(() => {
    let strength: PasswordStrength = checkPasswordStrength(newPassword);
    passStrength = strength.power;

    if (strength.power < 100) {
      passMessage = strength.message;
    } else {
      passMessage = undefined;
    };

  }, 100);


  async function handleReset() {

    warnUser = false;

    if (showReset) {
      let resetResponse = await resetPassword(passStrength, username as string, newPassword) as PasswordReturn;

      if (resetResponse.warnUser) {
        warnUser = resetResponse.warnUser;
        errorMessage = resetResponse.error;
        goTop();
        return;
      } else {
        toastStore.trigger(t);

        // sleep so toast can be seen
        await sleep(2000);

        // clear temp token
        authManager.clearToken();

        // redirect
        goto(CommonPaths.LOGIN);
        return;
      }
    }

    if (secretAnswer !== '') {
      let tokenReturn = await getToken(username as string, secretAnswer) as TokenReturn;

      if (!tokenReturn.token) {
        warnUser = tokenReturn.warnUser;
        errorMessage = tokenReturn.error;
        goTop();
        return;
      } else {
        // show reset option now that user has been verified
        showReset = true;
        goTop();
        return;
      }

    } else {
      let response = await getSecurity(username as string) as SecurityReturn;
      if (response.warnUser) {
        warnUser = response.warnUser;
        errorMessage = response.error;
        goTop();

      } else {
        warnUser = response.warnUser
        secretQuestion = response.question!;
      }

    }

  }

  
</script>

<section class="pt-24 border-gray-100 col-span-full flex-1 pb-16 md:pb-0 items-center">

  {#if warnUser}
    <LoginWarning
    errorMessage={errorMessage}
    />
  {/if}

  <form class="z-10 mx-auto rounded-2xl bg-slate-100 border shadow p-4 md:w-96 md:px-5" on:submit|preventDefault={handleReset}>

    <img alt="OpsML logo" class="mx-auto -mt-12 mb-2 w-20" src={logo}>
    <h1 class="pt-1 text-center text-3xl font-bold text-primary-500">Password Reset</h1>
    
    <div class="mb-8 grid grid-cols-1 gap-3">

      {#if !secretQuestion && !showReset}
        <label class="text-primary-500">Username
          <p class="mb-1 text-gray-500 text-xs">Username or Email associated with account</p>
          <input
            class="input rounded-lg bg-slate-200 hover:bg-slate-100"
            type="text" 
            placeholder="Username"
            bind:value={username}
          />
        </label>
      {/if}

      {#if secretQuestion && !showReset}
        <label class="text-primary-500">Secret Question
          <input
            class="input rounded-lg bg-slate-200 hover:bg-slate-100"
            type="text" 
            placeholder="Secret question"
            bind:value={secretQuestion}
          />
        </label>

        <label class="text-primary-500">Secret Answer
          <input
            class="input rounded-lg bg-slate-200 hover:bg-slate-100"
            type="text" 
            placeholder="Secret answer"
            bind:value={secretAnswer}
          />
        </label>
      {/if}

      {#if showReset}
        <label class="text-primary-500">New Password
          <p class="mb-1 text-gray-500 text-xs">Provide new password. Temporary token will expire in 5 minutes.</p>
          <input
            class="input rounded-lg bg-slate-200 hover:bg-slate-100"
            type="text" 
            placeholder="New Password"
            on:keydown={checkPassword}
            bind:value={newPassword}
          />

          <div class="mt-2">
            <p class="text-xs text-primary-400">Password Strength</p>
            {#if passMessage}
              <p class="text-xs text-primary-400 mb-0.5">{passMessage}</p>
            {/if}
            <ProgressBar meter="bg-secondary-600" value={passStrength} />
          </div>
        </label>
      {/if}

    </div>

    <div class="grid justify-items-center">
      <button type="submit" class="btn bg-primary-500 text-white rounded-lg md:w-72 justify-self-center mb-2">
        <span>Submit</span>
      </button>
    </div>
  </form>
</section>