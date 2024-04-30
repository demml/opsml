<script>
  import "../app.css";
  import "github-markdown-css/github-markdown-light.css";
  import Navbar from "$lib/Navbar.svelte";
  import favicon from "$lib/images/opsml-green.ico";
  import { initializeStores, Toast } from '@skeletonlabs/skeleton';

  initializeStores();
  

</script>

<svelte:head>
  <link rel="icon" type="image/x-icon" href={favicon}/>
</svelte:head>

<Toast />

<div class="bg-cover bg-center layout overflow-auto min-h-screen" id="page">
    <Navbar />
    <slot></slot>
</div>
