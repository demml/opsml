<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import logo from "$lib/images/opsml_word.png";
  import { page } from "$app/stores";
  import { popup, type PopupSettings } from '@skeletonlabs/skeleton';
  import { loadModal } from "$lib";
  import type { ModalComponent, ModalSettings, ModalStore } from '@skeletonlabs/skeleton';
  import LogoutModal from "$lib/components/LogoutModal.svelte";
  import { goto } from "$app/navigation";
  import Fa from 'svelte-fa'
  import { faUser } from '@fortawesome/free-solid-svg-icons'
  import { browser } from '$app/environment';
  import { authManager, loggedIn } from "./scripts/auth/authManager";

  let popupMessage: string = "";
  export let needAuth: boolean = false;
  export let isLoggedIn: boolean = false;

  let hamburger;
  let hamburgerOptions;
  let isOptionsVisible = false;


  const modalStore: ModalStore = loadModal();

  const popupAuth: PopupSettings = {
		event: 'hover',
		target: 'popupAuth',
		placement: 'bottom'
	};

  const popupUser: PopupSettings = {
		event: 'click',
		target: 'popupUser',
		placement: 'bottom'
	};

  function logInHandle() {
    const currentPage = $page.url.pathname;
    goto('/opsml/auth/login?url=' + currentPage);
  }

  async function logOut() {

    const modalComponent: ModalComponent = {
    ref: LogoutModal,
    props: { 
      modalStore: modalStore
    },
  };

		const modal: ModalSettings = {
			type: 'component',
      component: modalComponent,
		};
		modalStore.trigger(modal);
  }

  function toggleOptions() {
    isOptionsVisible = !isOptionsVisible;
    hamburgerOptions.style.display = isOptionsVisible ? 'block' : 'none';
  }

  function closeOptions() {
    isOptionsVisible = false;
    hamburgerOptions.style.display = 'none';
  }

  function navigateToPath(name: string) {
    let path = `/opsml/${name}`
    closeOptions();
    goto(path);
  }


  function handleClickOutside(event) {
    if (
      isOptionsVisible &&
      hamburger &&
      hamburgerOptions &&
      !hamburger.contains(event.target) &&
      !hamburgerOptions.contains(event.target)
    ) {
      hamburgerOptions.style.display = 'none';
    }
  }


  onMount(() => {
    if (browser) {
      document.addEventListener('click', handleClickOutside);
    }

  });

  onDestroy(() => {
    if (browser) {
      document.removeEventListener('click', handleClickOutside);
    }
  });


  const names = ["Models", "Data", "Runs"];

  if (needAuth) {
    popupMessage = "Login to access OpsML features";
  } else {
    popupMessage = "Authentication not required";
  }

  

</script>

<div class="card p-2 w-48 bg-surface-200 shadow-xl rounded-2xl border border-primary-500 border-solid" data-popup="popupAuth">
    <p class="text-sm text-primary-500 text-center">{popupMessage}</p>
  <div class="arrow bg-surface-100-800-token"></div>
</div>

<div class="card mt-3 w-40 shadow-xl bg-white z-10 rounded-lg" data-popup="popupUser">
	<div>
    <p class="text-sm font-bold text-primary-500 px-2 pl-2 py-1 rounded-t-lg border-dashed text-center">Options</p>
    
    <p class="w-32 mx-4 border-b-2 border-primary-500" />

    <div class="flex flex-col p-2">
        <div class="mr-1 ml-0.5 flex items-center overflow-hidden whitespace-nowrap text-sm leading-tight">
          <svg class="w-5 h-5 text-gray-800 flex-none w-3 mr-1 fill-primary-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24">
            <path fill-rule="evenodd" d="M17 10v1.126c.367.095.714.24 1.032.428l.796-.797 1.415 1.415-.797.796c.188.318.333.665.428 1.032H21v2h-1.126c-.095.367-.24.714-.428 1.032l.797.796-1.415 1.415-.796-.797a3.979 3.979 0 0 1-1.032.428V20h-2v-1.126a3.977 3.977 0 0 1-1.032-.428l-.796.797-1.415-1.415.797-.796A3.975 3.975 0 0 1 12.126 16H11v-2h1.126c.095-.367.24-.714.428-1.032l-.797-.796 1.415-1.415.796.797A3.977 3.977 0 0 1 15 11.126V10h2Zm.406 3.578.016.016c.354.358.574.85.578 1.392v.028a2 2 0 0 1-3.409 1.406l-.01-.012a2 2 0 0 1 2.826-2.83ZM5 8a4 4 0 1 1 7.938.703 7.029 7.029 0 0 0-3.235 3.235A4 4 0 0 1 5 8Zm4.29 5H7a4 4 0 0 0-4 4v1a2 2 0 0 0 2 2h6.101A6.979 6.979 0 0 1 9 15c0-.695.101-1.366.29-2Z" clip-rule="evenodd"/>
          </svg>
          <a class="truncate text-black hover:text-primary-500" href="/opsml/auth/update">Update Profile</a>
        </div>
      </div>
    </div>
</div>




<div class="bg-primary-500" id="header">

  <div class="mx-auto px-4 container relative flex h-16 items-center">

    <div class="flex flex-1 items-center">

      <a href="/opsml/index" >
        <div class="hidden flex items-center lg:mr:6 md:block">
          <img src={logo} class="h-5 sm:h-10" alt="Opsml Logo" />
          <span class="self-center text-2xl font-semibold whitespace-nowrap dark:text-white"></span>
        </div>
      </a>
    </div>

    {#if needAuth && isLoggedIn === true  || !needAuth}
     
      <nav id="navbar">
        <ul class="flex items-center space-x-2 xl:space-x-3">
          {#each names as name}
            {@const path = '/opsml/' + name.replace(/s$/, '').toLowerCase()}
            <li class="hidden md:block">
                <a class="group flex items-center md:text-lg text-white active:font-bold" href={path} class:active={$page.url.pathname.includes(path)}>
                  {name}
                </a>
            </li>
          {/each}
          <li class="hidden md:block">
            <a class="group flex items-center md:text-lg text-white active:font-bold" href='https://thorrester.github.io/opsml-ghpages/'>
              Docs
            </a>
          </li>

          <li>
            <div class="relative-group">
              <button id="hamburger" bind:this={hamburger} on:click={toggleOptions} type="button" class="inline-flex items-center w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden" aria-controls="navbar-default" aria-expanded="false">
                <span class="sr-only">Open main menu</span>
                <svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 17 14">
                    <path stroke="white" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 1h15M1 7h15M1 13h15"/>
                </svg>
              </button>
              <div bind:this={hamburgerOptions} class="hidden absolute top-full z-10 mt-1 w-32 min-w-0 max-w-xs overflow-hidden rounded-xl card bg-primary-50" id="hamburger-options">
                <section class="p-4 pb-5 space-y-4 overflow-y-auto">
                  <p class="font-bold text-lg">Opsml</p>
                  <nav class="list-nav">
                    <ul>
                      {#each names as name}

                        <li>
                          <button on:click={() => navigateToPath(name.replace(/s$/, '').toLowerCase())}>
                            <span class="flex-auto">{name}</span>
                          </button>
                        </li>
                      {/each}
                  </nav>
                </section>
              </div>
            </div>
          </li>
        </ul>
      </nav>
    {/if}

    <div class="flex items-center border-l border-slate-200 ml-4 mr-4 pl-2">
      <a href="https://github.com/shipt/opsml" class="ml-2 block text-slate-400 hover:text-slate-500">
        <span class="sr-only">Opsml on GitHub</span>
        <svg viewBox="0 0 16 16" class="w-6 h-6 fill-white" aria-hidden="true">
          <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
        </svg>
      </a>
    </div>


    {#if isLoggedIn === false}
      <button class="items-center md:text-lg text-white active:font-bold hover:font-bold" on:click={logInHandle} use:popup={popupAuth}>Login</button>
    {:else}

      <div class="flex items-center gap-x-2">
        <button  use:popup={popupUser}>
          <Fa size='1x' icon={faUser} color="white"/>
        </button>
        <button class="items-center md:text-lg text-white active:font-bold hover:font-bold" on:click={() => logOut()}>Logout</button>
      </div>
    {/if}

  </div>
</div>


<style>

  nav a:focus {
    text-decoration: underline;
    text-decoration-color: rgb(26, 255, 163);
    text-underline-offset: 1em;
    font-weight: 700;
  }

  nav a:hover {
    text-decoration: underline;
    text-decoration-color: rgb(26, 255, 163);
    text-underline-offset: 1em;
    font-weight: 700;
  }

  nav a.active {
    text-decoration: underline;
    text-decoration-color: rgb(26, 255, 163);
    text-underline-offset: 1em;
    font-weight: 700;
  }

</style>
