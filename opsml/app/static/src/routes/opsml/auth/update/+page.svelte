
<script lang="ts">
    import { goto } from "$app/navigation";
    import logo from "$lib/images/opsml-logo.png";
    import { type RegisterUser } from "$lib/scripts/types";
    import { registerUser, type RegisterResponse } from "$lib/scripts/register";
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
  
    async function handleUser() {
      // Handle login logic here
      // check if email and password are not empty
      if (username === '') {
        warnUser = true;
        errorMessage = 'Check all inputs. Username or email cannot be none.';
        return;
      }
  
      let user = {
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


  <form class="z-10 mx-auto rounded-2xl bg-slate-100 border shadow p-4 md:w-96 md:px-5" on:submit|preventDefault={handleUser}>

    <img alt="OpsML logo" class="mx-auto -mt-12 mb-2 w-20" src={logo}>
    <h1 class="pt-1 text-center text-3xl font-bold text-primary-500">Reset Password</h1>
    
    <div class="mb-8 grid grid-cols-1 gap-3">

      <label class="text-primary-500">Username or Email
        <p class="mb-1 text-gray-500 text-xs">Provide a username or email associated with account</p>
        <input
          class="input rounded-lg bg-slate-200 hover:bg-slate-100"
          type="text" 
          placeholder="Username"
          bind:value={username}
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