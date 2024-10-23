<script lang="ts">
  import "../app.css";
  import "github-markdown-css/github-markdown-light.css";
  import Navbar from "$lib/Navbar.svelte";
  import favicon from "$lib/images/opsml-green.ico";
  import { initializeStores, Toast, Modal, storePopup } from '@skeletonlabs/skeleton';
  import { computePosition, autoUpdate, offset, shift, flip, arrow } from '@floating-ui/dom';
  import { checkAuthstore } from "$lib/scripts/auth/authStore";
  import { loginStore } from "$lib/scripts/store";
  import { onMount } from "svelte";
  import { a } from "vitest/dist/suite-IbNSsUWN.js";


  storePopup.set({ computePosition, autoUpdate, offset, shift, flip, arrow });
  initializeStores();

  /** @type {import('./$types').LayoutData} */
	export let data;

  $: authStore = data.authStore;


  checkAuthstore(authStore);
  
</script>

<svelte:head>
  <link rel="icon" type="image/x-icon" href={favicon}/>
</svelte:head>

<Toast />
<Modal />

<div class="bg-cover bg-center layout overflow-auto min-h-screen" id="page">
    <Navbar 
      needAuth={authStore.needAuth()}
      loggedIn={authStore.loggedIn}
    />
    <slot></slot>
</div>
