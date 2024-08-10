
<script lang="ts">
  import { goto } from "$app/navigation";
  import { CommonPaths, type UserResponse, type User, type UpdateUserRequest, type UpdateUserResponse } from "$lib/scripts/types";
  import { authStore } from "$lib/scripts/authStore";
  import { updateUser, goTop } from "$lib/scripts/utils";
  import { onMount } from "svelte";
  import { getUser } from "$lib/scripts/utils";
  import logo from "$lib/images/opsml-logo.png";
  import LoginWarning from "$lib/components/LoginWarning.svelte";
  import { getToastStore, type ToastSettings } from '@skeletonlabs/skeleton';


    // toast
    const toastStore = getToastStore();

    const t: ToastSettings = {
      message: 'User profile updated',
    };

  
  
    /** @type {import('./$types').PageData} */
    let user: User;
    let currentUsername = authStore.getUsername() as string;
    let username = authStore.getUsername();
    let password = '';
    let newPassword = '';
    let email = '';
    let fullName = '';
    let securityAnswer = '';
    let securityQuestion = '';
    let errorMessage = '';
    let warnUser: boolean = false;


    onMount(() => {
    
      let loggedIn = authStore.loggedIn();

      if (loggedIn === "true") {
        // get user data
        getUser(authStore.getUsername() as string).then((response: UserResponse) => {
          user = response.user as User;
          if (user.email) email = user.email;
          if (user.full_name) fullName = user.full_name;
          if (user.security_question) securityQuestion = user.security_question;
          if (user.security_answer) securityAnswer = user.security_answer;
        });

      } else {
        goto(CommonPaths.LOGIN + "?redirect=" + CommonPaths.UPDATE);
      }
  });

  async function handleUpdate() {

    // validate provided password
    // need to use original username to validate password
    let valid = await authStore.loginWithCredentials(currentUsername, password);

    if (!valid) {
      warnUser = true;
      errorMessage = 'Invalid password. Please provide correct password.';
      goTop();
      return;
    }

    warnUser = false;

    if (newPassword !== '') {
      password = newPassword;
    };

  
    let request: UpdateUserRequest = {
      username: currentUsername,
      updated_username: null,
      password: password,
      email: email,
      full_name: fullName,
      security_question: securityQuestion,
      security_answer: securityAnswer,
      scopes: user.scopes,
      is_active: user.is_active,
    }

    if (username !== currentUsername) {
      request.updated_username = username;
    }


    let response: UpdateUserResponse = await updateUser(request);

    if (response.updated) {
      // set new user and pass to local storage
      let valid = await authStore.loginWithCredentials(username as string, password);
      if (!valid) {
        warnUser = true;
        errorMessage = 'User profile updated but could not login with new credentials. Please try again or contact your admin.';
        goTop();
        return;
      }

      // Reroute to home
      warnUser = false;
      errorMessage = '';
      
      toastStore.trigger(t);
      goto(CommonPaths.HOME);
  

    } else {
      errorMessage = 'Could not update user profile. Please try again or contact your admin.';
      warnUser = true;
      goTop();
      return;
    }


}

</script>

<section class="pt-24 border-gray-100 col-span-full flex-1 pb-16 items-center">
  {#if warnUser}
    <LoginWarning
    errorMessage={errorMessage}
    />
  {/if}
  <form class="z-10 mx-auto rounded-2xl bg-slate-100 border shadow p-4 md:w-96 md:px-5" on:submit|preventDefault={handleUpdate}>

    <img alt="OpsML logo" class="mx-auto -mt-12 mb-2 w-20" src={logo}>
    <h1 class="pt-1 text-center text-3xl font-bold text-primary-500">Update User Profile</h1>
    <p class="mb-1 text-gray-500 text-xs text-center">
      Update any of the following parameters and click update. Leave defaults or blanks if you do not wish to update.
    </p>
    
    <div class="mb-8 grid grid-cols-1 gap-3">

      <label class="text-primary-500">Username
        <p class="mb-1 text-gray-500 text-xs">Username</p>
        <input
          class="input rounded-lg bg-slate-200 hover:bg-slate-100"
          type="text" 
          placeholder="Username"
          bind:value={username}
        />
      </label>

      <label class="text-primary-500">Full name
        <p class="mb-1 text-gray-500 text-xs">Full name to associate with user</p>
        <input
          class="input rounded-lg bg-slate-200 hover:bg-slate-100"
          type="text" 
          placeholder="Full name"
          bind:value={fullName}
        />
      </label>

      <label class="text-primary-500">Email
        <p class="mb-1 text-gray-500 text-xs">Email associated with profile</p>
        <input
          class="input rounded-lg bg-slate-200 hover:bg-slate-100"
          type="text" 
          placeholder="Email"
          bind:value={email}
        />
      </label>

      <label class="text-primary-500">Current Password
        <p class="mb-1 text-gray-500 text-xs">Current password (required)</p>
        <input
          class="input rounded-lg bg-slate-200 hover:bg-slate-100"
          type="text" 
          placeholder="Password"
          bind:value={password}
        />
      </label>

      <label class="text-primary-500">New Password
        <p class="mb-1 text-gray-500 text-xs">New password you wish to use</p>
        <input
          class="input rounded-lg bg-slate-200 hover:bg-slate-100"
          type="text" 
          placeholder="Password"
          bind:value={newPassword}
        />
      </label>

      <label class="text-primary-500">Security Question
        <p class="mb-1 text-gray-500 text-xs">Select security question for password recovery</p>
        <select class="select rounded-lg bg-slate-200 hover:bg-slate-100" bind:value={securityQuestion}>
          <option value="In what city were you born?">In what city were you born?</option>
          <option value="What is you favorite machine learning library?">What is you favorite machine learning library?</option>
          <option value="What is your favorite movie?">What is your favorite movie?</option>
          <option value="Give me something random">Give me something random</option>
        </select>
      </label>

      <label class="text-primary-500">Answer
        <p class="mb-1 text-gray-500 text-xs">Answer to security question</p>
        <input
          class="input rounded-lg bg-slate-200 hover:bg-slate-100"
          type="text" 
          placeholder="Answer"
          bind:value={securityAnswer}
        />
      </label>
    </div>

    <div class="grid justify-items-center">
      <button type="submit" class="btn bg-primary-500 text-white rounded-lg md:w-72 justify-self-center mb-2">
        <span>Update</span>
      </button>
    </div>
  </form>
</section>