<script lang="ts">
    import "../app.css";
    import "github-markdown-css/github-markdown-light.css";
    import favicon from "$lib/images/opsml-green.ico";
    import Navbar from "$lib/components/nav/Navbar.svelte";
    import lightningBolt from "$lib/images/lightningbolt.webp";
    import { onMount } from 'svelte';


    let { children } = $props();
  
    let show = $state(false);
    
    onMount(() => {
        setTimeout(() => {
          show = true;
        }, 50);
    });


  </script>
  
  <svelte:head>
    <link rel="icon" type="image/x-icon" href={favicon}/>
  </svelte:head>

{#if show}
  <div class="layout overflow-auto min-h-screen font-sans" id="page">
    <Navbar/>
    {@render children()}
  </div>
{:else}
  <div class="flex items-center justify-center min-h-screen">
      <div class="animate-spin h-8 w-8 border-4 border-primary-500 rounded-full border-t-transparent"></div>
  </div>
{/if}
