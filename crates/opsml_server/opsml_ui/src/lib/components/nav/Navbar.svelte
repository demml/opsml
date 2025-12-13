<script lang="ts">
  import { onMount } from "svelte";
  import logo from "$lib/images/opsml_word.webp";
  import { page } from "$app/state";
  import { goto } from "$app/navigation";
  import { KeySquare } from 'lucide-svelte';
  import UserDropdown from "../user/UserDropdown.svelte";
  import { uiSettingsStore } from '$lib/components/settings/settings.svelte';

  let isSidebarOpen = $state(false);

  function logInHandle() {
    const currentPage = page.url.pathname;
    goto('/opsml/user/login?url=' + currentPage);
  }

  let imageLoaded = $state(false);
  let scouterEnabled = $derived(uiSettingsStore.scouterEnabled);

  const names = ["Spaces", "Models", "Data", "GenAI", "Experiments", "Services", "Observability"];


  onMount(() => {
    const img = new Image();
    img.src = logo;
    img.onload = () => {
      imageLoaded = true;
    };
  });

</script>

<nav class="fixed left-0 top-0 z-20 mx-auto flex w-full items-center border-b-4 border-border bg-primary-700 border-b-2 border-black px-5 h-14">
  <div class="mx-auto flex w-full items-center justify-between px-8 lg:px-10">

    <div class="hidden md:block">
      <div class="flex items-center justify-start gap-4">
        <a href="/opsml/home" class="items-center">
          <div class="w-[120px] h-10">
            <img
              src={logo}
              class="h-10 w-[120px] object-contain"
              alt="Opsml Logo"
            />
          </div>
        </a>

        <div class="flex items-center gap-2 md:gap-4 lg:gap-6">
          {#each names as name}
            {@const path = '/opsml/' + name.replace(/s$/, '').toLowerCase()}
              <a href={path} class:active={page.url.pathname.includes(path)} data-sveltekit-preload-data="hover">
                {name}
              </a>
          {/each}
        </div>
      </div>
    </div>

    <div class="flex items-center justify-end gap-4 m800:w-[unset] m400:gap-2">

      <a aria-label="github" href="https://github.com/demml/opsml" class="m800:hidden flex gap-2 items-center justify-center rounded-base border-2 border-black shadow p-2 shadow-hover bg-surface-50 w-9 h-9">
        <svg
          role="img"
          viewBox="0 0 24 24"
          width="24"
            height="24"
            xmlns="http://www.w3.org/2000/svg">
            <title>GitHub</title>
            <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>
          </svg>
      </a>

        <button aria-label="login" onclick={logInHandle} class="m800:hidden flex gap-2 items-center justify-center rounded-base border-2 border-black shadow p-2 shadow-hover bg-surface-50 w-9 h-9">
          <KeySquare color="#5948a3"/>
        </button>

        <div
          aria-label="user"
          class="m800:hidden relative flex items-center justify-center rounded-base border-2 border-black shadow p-2 shadow-hover bg-surface-50 w-9 h-9"
        >
          <UserDropdown/>
        </div>
      </div>
  </div>
</nav>



<style>


  nav a:focus {
    text-decoration: underline;
    text-decoration-color: rgb(26, 255, 163);
    text-underline-offset: .75em;
  }

  nav a:hover {
    text-decoration: underline;
    text-decoration-color: rgb(26, 255, 163);
    text-underline-offset: .75em;
  }

  nav a.active {
    text-decoration: underline;
    text-decoration-color: rgb(26, 255, 163);
    text-underline-offset: .75em;
    font-weight: 700;
  }

</style>
