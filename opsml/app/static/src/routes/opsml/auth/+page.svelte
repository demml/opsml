
<script>
  import Input from '$lib/components/LoginInput.svelte';
  import Button from '$lib/components/LoginButton.svelte';
  import logo from "$lib/images/opsml-logo.png";

  let email = '';
  let password = '';

  function handleSubmit() {
    // Handle login logic here
    console.log('Login submitted', { email, password });
  }
</script>

<div class="min-h-screen flex flex-col md:grid md:space-y-0 w-full h-full md:grid-cols-12 md:flex-1 md:grid-rows-full space-y-4 md:gap-6 max-w-full max-h-full bg-gradient-to-b from-surface-500 via-secondary-200 via-70% to-white">
  <section class="pt-24 border-gray-100 col-span-full flex-1 pb-16 md:pb-0 items-center">
    <form class="z-10 mx-auto rounded-2xl bg-slate-100 border shadow p-4 md:w-96 md:px-5" on:submit|preventDefault={handleSubmit}>

      <img alt="OpsML logo" class="mx-auto -mt-12 mb-2 w-20" src={logo}>
      <h1 class="pt-1 text-center text-3xl font-bold text-primary-500">Log In</h1>
      <p class="mb-6 text-center text-gray-500">New to OpsML?
        <a class="underline hover:text-primary-700" href="#">Register</a>
      </p>

      <div class="mb-8 grid grid-cols-1 gap-3">
        <label class="text-primary-500">Username or Email address
          <input
            class="input rounded-lg bg-slate-200 hover:bg-slate-100"
            type="text" 
            placeholder="Email"
            bind:value={email}
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
        <button type="button" class="btn bg-primary-500 text-white rounded-lg md:w-72 justify-self-center mb-2">
          <span>Login</span>
        </button>
        <a class="text-primary-500 hover:text-primary-700" href="#">Forgot password?</a>
      </div>
    </form>
  </section>
</div>