
<script lang="ts">
    import { goto } from "$app/navigation";
    import logo from "$lib/images/opsml-logo.png";
    import { type RegisterUser } from "$lib/scripts/types";
    import { registerUser, type RegisterResponse } from "$lib/scripts/register";
    import LoginWarning from "$lib/components/LoginWarning.svelte";
    import { CommonPaths } from "$lib/scripts/types";
    import { authStore } from "$lib/authStore";
    import { onMount } from "svelte";
  
    /** @type {import('./$types').PageData} */
    export let data;
    let updateType = data.type;

    onMount(() => {
    
      let loggedIn = authStore.loggedIn();

      if (loggedIn === "true") {
        // validate user
      } else {
        goto(CommonPaths.LOGIN + "?redirect=" + CommonPaths.UPDATE);
      }
  });

  </script>

<section class="pt-24 border-gray-100 col-span-full flex-1 pb-16 items-center">
  hello
</section>