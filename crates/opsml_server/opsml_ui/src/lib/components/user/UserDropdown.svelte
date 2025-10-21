<script lang="ts">
  import { UserRound } from "lucide-svelte";
  import { userStore } from "./user.svelte";


  let isOpen = $state(false);

  function toggleDropdown() {
      isOpen = !isOpen;
  }

  // Close dropdown when clicking outside
  function handleClickOutside(event: MouseEvent) {
      const target = event.target as HTMLElement;
      if (!target.closest('.dropdown')) {
          isOpen = false;
      }
  }

</script>


<svelte:window on:click={handleClickOutside}/>

<div class="dropdown w-full h-full">
    <button 
        type="button"
        onclick={toggleDropdown}
        class="w-full h-full flex items-center justify-center"
    >
        <UserRound color="#5948a3" size={24}/>
    </button>

    {#if isOpen}
      <div class="absolute right-0 mt-2 w-30 bg-primary-500 border-black border-2 rounded-lg shadow-lg z-50">
        <div class="border-b-2 border-black text-center text-black text-sm">User</div>
        <div class="flex flex-col">
          <a
              href={`/opsml/user/profile/${userStore.username}`}
              onclick={toggleDropdown}
              class="block px-1 m-1 text-left border-2 border-transparent hover:border-black rounded-lg transition-colors text-black text-sm"
          >
            Profile
          </a>
          <a
              href="/opsml/user/logout"
              onclick={toggleDropdown}
              class="block px-1 m-1 text-left border-2 border-transparent hover:border-black rounded-lg transition-colors text-black text-sm"
          >
            Logout
          </a>
        </div>
      </div>
    {/if}
</div>


