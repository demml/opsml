
<script lang="ts">
  import { goto } from "$app/navigation";
  import logo from "$lib/images/opsml-logo.png";
  import { authStore } from "$lib/scripts/authStore";
  import LoginWarning from "$lib/components/LoginWarning.svelte";
  import { updateLoginStore } from "$lib/scripts/store";
  import { CommonPaths, type UserExistsResponse } from "$lib/scripts/types";
  import { goTop} from "$lib/scripts/utils";
  import { checkUser } from "$lib/scripts/auth_routes";
  import { type securityQuestionResponse, CommonErrors, type PasswordStrength } from "$lib/scripts/types";
  import { onMount } from "svelte";
  import { getSecurityQuestion, generateTempToken } from "$lib/scripts/auth_routes";
  import { checkPasswordStrength, delay } from "$lib/scripts/utils";
  import { ProgressBar } from '@skeletonlabs/skeleton';

  let warnUser: boolean = false;
  let errorMessage: string = '';
  let passStrength = 0;
  let passMessage: string | null = null;

  /** @type {import('./$types').PageData} */
  export let data;
  let username: string | null = data.username;
  let secretQuestionRes: securityQuestionResponse | null = data.secretQuestion;
  let secretQuestion = secretQuestionRes?.question as string;
  let secretAnswer = '';
  let tokenResult: string = '';
  let showReset: boolean = false;
  let newPassword = '';

  let checkPassword = delay(() => {
    let strength: PasswordStrength = checkPasswordStrength(newPassword);
    passStrength = strength.power;

    if (strength.power < 100) {
      passMessage = strength.message;
    } else {
      passMessage = null;
    };

  }, 500);

  async function resetPassword() {
    if (passStrength < 100) {
      warnUser = true;
      errorMessage = 'Password is weak. Please provide a stronger password.';
      goTop();
      return;
    }

    console.log('resetting password');
  }

  async function getToken() {
    tokenResult = await generateTempToken(username as string, secretAnswer);
      if ([CommonErrors.USER_NOT_FOUND.toString(), CommonErrors.INCORRECT_ANSWER.toString(), CommonErrors.TOKEN_ERROR.toString()].includes(tokenResult)) {
        warnUser = true
        errorMessage = tokenResult;
        goTop();
        return;

      } else {
        showReset = true;
        goTop();
        return;
      }
  }

  async function getSecurity() {
    // reset warning
    warnUser = false;

    // Handle login logic here
    if (!username) {
      // check if username is not empty
      warnUser = true;
      errorMessage = 'Username cannot be empty';
      goTop();
      return;
    }

    let userExists: UserExistsResponse = await checkUser(username as string);

    if (!userExists.exists) {
      warnUser = true;
      errorMessage = 'User does not exist';
      goTop();
      return;
    }

    secretQuestionRes = await getSecurityQuestion(username);
    secretQuestion = secretQuestionRes?.question as string;

    if (secretQuestionRes) {
    if (!secretQuestionRes.exists) {
      warnUser = true;
      errorMessage = secretQuestionRes.error;
      goTop();
      return;
      }  
    }
  }
  

  async function handleReset() {

    warnUser = false;

    if (showReset) {
      await resetPassword();
    }
    if (secretAnswer !== '') {
      await getToken();
    } else {
      await getSecurity();
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

      {#if !secretQuestionRes && !showReset}
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

      {#if secretQuestionRes && !showReset}
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