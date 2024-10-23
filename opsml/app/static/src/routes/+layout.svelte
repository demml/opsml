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


  // async onMOunt
  onMount(async () => {
    let authstate = authManager.getAuthState();
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

  <Navbar/>
  <slot></slot>

</div>
