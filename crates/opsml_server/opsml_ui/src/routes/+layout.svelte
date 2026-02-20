<script lang="ts">
    import "../app.css";
    import "github-markdown-css/github-markdown-light.css";
    import favicon from "$lib/images/opsml-green.ico";
    import Navbar from "$lib/components/nav/Navbar.svelte";
    import { onMount } from 'svelte';
    import { ToastProvider } from '@skeletonlabs/skeleton-svelte';
    import { uiSettingsStore } from "$lib/components/settings/settings.svelte";


    let { data, children} = $props();
  
    // Re-initialize settings reactively so the store updates on every navigation
    // (e.g. when Scouter is disabled while the app is running)
    $effect(() => {
      uiSettingsStore.initialize(data.settings);
    });
    
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
  <div class="layout flex flex-col font-sans" id="page">
    <Navbar/>
      <ToastProvider 
        messageBase="text-base" 
        placement="top-end" 
        stateError="bg-error-500 justify-center text-black border-2 border-black" 
        stateSuccess="bg-secondary-500 text-black border-2 border-black">
        <div class="grid-background pt-14 min-h-screen">
          {@render children()}
        </div>
      </ToastProvider>
  </div>
{:else}
  <div class="flex items-center justify-center min-h-screen">
      <div class="animate-spin h-8 w-8 border-4 border-primary-500 rounded-full border-t-transparent"></div>
  </div>
{/if}


<style>
  .grid-background {
    background-color: #E3DFF2;
    background-image: 
      linear-gradient(to right, #CECBDB 1px, transparent 1px),
      linear-gradient(to bottom, #CECBDB 1px, transparent 1px);
    background-size: 60px 60px;
    background-attachment: fixed;
  }
</style>