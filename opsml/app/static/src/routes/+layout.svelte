<script lang="ts">
  import "../app.css";
  import "github-markdown-css/github-markdown-light.css";
  import Navbar from "$lib/Navbar.svelte";
  import favicon from "$lib/images/opsml-green.ico";
  import { initializeStores, Toast, Modal, storePopup } from '@skeletonlabs/skeleton';
  import { computePosition, autoUpdate, offset, shift, flip, arrow } from '@floating-ui/dom';
  import { checkAuthstore } from "$lib/authStore";
  import { loginStore } from "$lib/scripts/store";

  storePopup.set({ computePosition, autoUpdate, offset, shift, flip, arrow });
  initializeStores();

  /** @type {import('./$types').LayoutData} */
	export let data;
  let authStore = data.authStore;

  checkAuthstore(authStore, data.previousPath);
  
</script>

<svelte:head>
  <link rel="icon" type="image/x-icon" href={favicon}/>
</svelte:head>

<Toast />
<Modal />

<div class="bg-cover bg-center layout overflow-auto min-h-screen" id="page">
    <Navbar 
      needAuth={authStore.needAuth()}
      loggedIn={$loginStore}
    />
    <slot></slot>
</div>
