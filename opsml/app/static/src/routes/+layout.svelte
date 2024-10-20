<script lang="ts">
  import "../app.css";
  import "github-markdown-css/github-markdown-light.css";
  import Navbar from "$lib/Navbar.svelte";
  import favicon from "$lib/images/opsml-green.ico";
  import { initializeStores, Toast, Modal, storePopup } from '@skeletonlabs/skeleton';
  import { computePosition, autoUpdate, offset, shift, flip, arrow } from '@floating-ui/dom';
  import { authStore, type AuthState } from '$lib/scripts/auth/newAuthStore';
  import { setupAuth } from '$lib/scripts/auth/setupAuth';
  import { onMount } from 'svelte';
  import { goto } from "$app/navigation";
  import { CommonPaths } from "$lib/scripts/types";

  storePopup.set({ computePosition, autoUpdate, offset, shift, flip, arrow });
  initializeStores();

  let auth: AuthState;
  $: auth = $authStore;


  // Run setupAuth on mount
  onMount(async () => {
    await setupAuth();

    // Check if user is logged in
    if (auth.requireAuth && !auth.isAuthenticated) {
      goto(CommonPaths.LOGIN + "?redirect=" + window.location.pathname);
    }

  });
  
</script>

<svelte:head>
  <link rel="icon" type="image/x-icon" href={favicon}/>
</svelte:head>

<Toast />
<Modal />

<div class="bg-cover bg-center layout overflow-auto min-h-screen" id="page">
    <Navbar />
    <slot></slot>
</div>
