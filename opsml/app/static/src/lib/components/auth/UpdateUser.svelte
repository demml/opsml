<script lang="ts">
  import { goto } from "$app/navigation";
  import logo from "$lib/images/opsml-logo.png";
  import { type RegisterUser } from "$lib/scripts/types";
  import { registerUser, type RegisterResponse } from "$lib/scripts/auth/authRoutes";
  import LoginWarning from "$lib/components/LoginWarning.svelte";
  import { CommonPaths } from "$lib/scripts/types";

  let username = '';
  let password = '';
  let email = '';
  let fullName = '';
  let securityAnswer = '';
  let securityQuestion = '';
  let errorMessage = '';


  let warnUser: boolean = false;

  async function handleRegister() {
    // Handle login logic here
    // check if email and password are not empty
    if (username === '' || password === '' || securityAnswer === '' || email === '') {
      warnUser = true;
      errorMessage = 'Check all inputs. User, password and security answer cannot be none.';
      return;
    }

    let user: RegisterUser = {
      username: username,
      password: password,
      email: email,
      security_question: securityQuestion,
      security_answer: securityAnswer,
      full_name: fullName,
    }

    let response: RegisterResponse  = await registerUser(user);
    if (response.success) {
      warnUser = false;
      errorMessage = '';
      goto(CommonPaths.LOGIN);
    } else {
      errorMessage = response.message;
      warnUser = true;
    }

  }

 

</script>

  <section class="pt-24 border-gray-100 col-span-full flex-1 pb-16 items-center">

    {#if warnUser}
      <LoginWarning
      errorMessage={errorMessage}
      />
    {/if}


    <form class="z-10 mx-auto rounded-2xl bg-slate-100 border shadow p-4 md:w-96 md:px-5" on:submit|preventDefault={handleRegister}>

      <img alt="OpsML logo" class="mx-auto -mt-12 mb-2 w-20" src={logo}>
      <h1 class="pt-1 text-center text-3xl font-bold text-primary-500">Register</h1>
      
      <div class="mb-8 grid grid-cols-1 gap-3">

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
          <p class="mb-1 text-gray-500 text-xs">Provide an email</p>
          <input
            class="input rounded-lg bg-slate-200 hover:bg-slate-100"
            type="text" 
            placeholder="Email"
            bind:value={email}
          />
        </label>

        <label class="text-primary-500">Username
          <p class="mb-1 text-gray-500 text-xs">Provide a username</p>
          <input
            class="input rounded-lg bg-slate-200 hover:bg-slate-100"
            type="text" 
            placeholder="Username"
            bind:value={username}
          />
        </label>

        <label class="text-primary-500">Password
          <p class="mb-1 text-gray-500 text-xs">Provide a password</p>
          <input
            class="input rounded-lg bg-slate-200 hover:bg-slate-100"
            type="text" 
            placeholder="Password"
            bind:value={password}
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
          <span>Register</span>
        </button>
      </div>
    </form>
  </section>