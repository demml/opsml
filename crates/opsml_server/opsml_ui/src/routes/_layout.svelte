<script lang="ts">
    import "../app.css";
    import "github-markdown-css/github-markdown-light.css";
    import Navbar from "$lib/Navbar.svelte";
    import favicon from "$lib/images/opsml-green.ico";
    import { initializeStores, Toast, Modal, storePopup } from '@skeletonlabs/skeleton';
    import { computePosition, autoUpdate, offset, shift, flip, arrow } from '@floating-ui/dom';
    import { onMount } from "svelte";
    import { CommonPaths } from "$lib/scripts/types";
    import { goto } from "$app/navigation";

  
  
  
    storePopup.set({ computePosition, autoUpdate, offset, shift, flip, arrow });
    
    // async onMOunt
    onMount(() => {

  
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
  