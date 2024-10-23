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
  import { authManager } from "$lib/scripts/auth/authManager";



  storePopup.set({ computePosition, autoUpdate, offset, shift, flip, arrow });
  initializeStores();
  let authstate;


  // async onMOunt
  onMount(async () => {
    authstate = await authManager.setupAuth();
    console.log("layout");
    console.log(authstate);
    if (authstate.requireAuth && !authstate.isAuthenticated) {
      // redirect to login page with previous page as query param
      void goto(CommonPaths.LOGIN);
      // do nothing
    }
  

  });
  
</script>

<svelte:head>
  <link rel="icon" type="image/x-icon" href={favicon}/>
</svelte:head>

<Toast />
<Modal />

<div class="bg-cover bg-center layout overflow-auto min-h-screen" id="page">

  {#if authstate}
    <Navbar/>
  {/if}
  
  <slot></slot>

</div>
