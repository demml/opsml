
<script lang="ts">
  import { goto } from "$app/navigation";
  import logo from "$lib/images/opsml-logo.png";
  import { authStore } from "$lib/authStore";
  import LoginWarning from "$lib/components/LoginWarning.svelte";
  import { updateLoginStore } from "$lib/scripts/store";

  let username = '';
  let password = '';

  let showLoginError: boolean = false;

  /** @type {import('./$types').PageData} */
  export let data;
  let previousPath = data.previousPath;

  async function handleLogin() {
    // Handle login logic here
    console.log('Login submitted', { username, password });
    let loggedIn: boolean = await authStore.loginWithCredentials(username, password);

    if (loggedIn) {
      // need to reload the page to update the nav bar
      updateLoginStore();
      if (previousPath) {
        goto(previousPath);
      } else {
        goto('/opsml');
      }
    } else {
      showLoginError = true;
    }

  }

  function handleRegister() {
    // Handle register logic here
    goto('/opsml/auth/register?url=' + previousPath);

  }
</script>

<div class="min-h-screen flex flex-col md:grid md:space-y-0 w-full h-full md:grid-cols-12 md:flex-1 md:grid-rows-full space-y-4 md:gap-6 max-w-full max-h-full bg-gradient-to-b from-surface-500 via-secondary-200 via-70% to-white">
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
        <button class="underline hover:text-primary-700" on:click={handleRegister}>Register</button>
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

      <div class="grid justify-items-center">
        <button type="submit" class="btn bg-primary-500 text-white rounded-lg md:w-72 justify-self-center mb-2">
          <span>Login</span>
        </button>
        <a class="text-primary-500 hover:text-primary-700" href="#">Forgot password?</a>
      </div>
    </form>
  </section>
</div>