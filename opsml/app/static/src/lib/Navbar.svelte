<script lang="ts">
  import { onMount } from "svelte";
  import js from "jquery";
  import logo from "$lib/images/opsml_word.png";
  import { page } from "$app/stores";
  import { popup, type PopupSettings } from '@skeletonlabs/skeleton';
  import { loadModal } from "$lib";
  import type { ModalComponent, ModalSettings, ModalStore } from '@skeletonlabs/skeleton';
  import LogoutModal from "$lib/components/LogoutModal.svelte";
  import { goto } from "$app/navigation";

  export let needAuth: boolean;
  export let loggedIn: string;
  let popupMessage: string = "";

  const modalStore: ModalStore = loadModal();

  const popupAuth: PopupSettings = {
		event: 'hover',
		target: 'popupAuth',
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

  onMount(() => {
    // @ts-ignore
    window.jq = js;

    // @ts-ignore
    window.jq("#hamburger").click(() => {

      // @ts-ignore
      window.jq("#hamburger-options").toggle();
    });
  });

  const names = ["Models", "Data", "Runs", "Audits"];

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

<div class="shadow-lg bg-primary-500" id="header">

  <div class="mx-auto px-4 container relative flex h-16 items-center">

    <div class="flex flex-1 items-center">

      <a href="/opsml/index" >
        <div class="hidden flex items-center lg:mr:6 md:block">
          <img src={logo} class="h-5 sm:h-10" alt="Opsml Logo" />
          <span class="self-center text-2xl font-semibold whitespace-nowrap dark:text-white"></span>
        </div>
      </a>
    </div>
    <nav id="navbar">
      <ul class="flex items-center space-x-2 xl:space-x-3">
        {#each names as name}
          {@const path = '/opsml/' + name.replace(/s$/, '').toLowerCase()}
          <li class="hidden md:block">
              <a class="group flex items-center text-white text-base text-lg md:text-xl active:font-bold" href={path} class:active={$page.url.pathname.includes(path)}>
                {name}
              </a>
          </li>
        {/each}
        <li class="hidden md:block">
          <a class="group flex items-center text-white text-base text-lg md:text-xl active:font-bold" href='https://thorrester.github.io/opsml-ghpages/'>
            Docs
          </a>
        </li>

        <li>
          <div class="relative-group">
            <button id="hamburger" type="button" class="inline-flex items-center w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden" aria-controls="navbar-default" aria-expanded="false">
              <span class="sr-only">Open main menu</span>
              <svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 17 14">
                  <path stroke="white" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 1h15M1 7h15M1 13h15"/>
              </svg>
            </button>
            <div class="hidden absolute top-full z-10 mt-1 w-32 min-w-0 max-w-xs overflow-hidden rounded-xl card bg-primary-50" id="hamburger-options">
              <section class="p-4 pb-5 space-y-4 overflow-y-auto">
                <p class="font-bold text-xl">Opsml</p>
                <nav class="list-nav">
                  <ul>
                    {#each names as name}
                      <li>
                        <a href='/opsml/{name.replace(/s$/, '').toLowerCase()}'>
                          <span class="flex-auto">{name}</span>
                        </a>
                      </li>
                    {/each}
                </nav>
              </section>
            </div>
          </div>
        </li>

      </ul>

    </nav>

    <div class="flex items-center border-l border-slate-200 ml-4 mr-4 pl-2">
      <a href="https://github.com/shipt/opsml" class="ml-2 block text-slate-400 hover:text-slate-500">
        <span class="sr-only">Opsml on GitHub</span>
        <svg viewBox="0 0 16 16" class="w-6 h-6 fill-white" aria-hidden="true">
          <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
        </svg>
      </a>
    </div>


    {#if loggedIn === 'false'}
      <button class="items-center text-white text-lg md:text-xl active:font-bold hover:font-bold" on:click={logInHandle} use:popup={popupAuth}>Login</button>
    {:else}
      <button class="items-center text-white text-lg md:text-xl active:font-bold hover:font-bold" on:click={() => logOut()}>Logout</button>
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
