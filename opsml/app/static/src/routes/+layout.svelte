<script lang="ts">
  import "../app.css";
  import "github-markdown-css/github-markdown-light.css";
  import Navbar from "$lib/Navbar.svelte";
  import favicon from "$lib/images/opsml-green.ico";
  import { initializeStores, Toast, Modal, storePopup } from '@skeletonlabs/skeleton';
  import { computePosition, autoUpdate, offset, shift, flip, arrow } from '@floating-ui/dom';
  import { onMount } from "svelte";
  import { type AuthState } from "$lib/scripts/auth/authManager"
  import { CommonPaths } from "$lib/scripts/types";
  import { goto } from "$app/navigation";
  import { authManager, checkAuthstore, loggedIn } from "$lib/scripts/auth/authManager";
  import { sleep } from "$lib/scripts/utils";



  storePopup.set({ computePosition, autoUpdate, offset, shift, flip, arrow });
  initializeStores();
  
  let isLoggedIn: boolean = false;

  let authstate: AuthState | undefined;
  $: authstate = undefined;

  // async onMOunt
  onMount(() => {


    (async () => {
      await checkAuthstore();
      authstate = authManager.getAuthState();
    })();

    // set the isLoggedIn value
    loggedIn.set({ isLoggedIn: authstate!.isAuthenticated });

    const unsubscribe = loggedIn.subscribe(value => {
      isLoggedIn = value.isLoggedIn;
    });

    

    return () => {
      unsubscribe();
    };

  });
  
</script>

<svelte:head>
  <link rel="icon" type="image/x-icon" href={favicon}/>
</svelte:head>

<Toast />
<Modal />


<div class="bg-cover bg-center layout overflow-auto min-h-screen" id="page">

  {#if authstate}
    <Navbar 
    isLoggedIn={isLoggedIn}
    needAuth={authstate.requireAuth}/>
  {/if}

  <slot></slot>

</div>
