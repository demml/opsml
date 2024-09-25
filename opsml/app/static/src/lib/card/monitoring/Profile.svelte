<script lang="ts">
    import { type DriftConfig, type AlertConfig } from "$lib/scripts/types";

    export let showProfile = false;

    async function handleUpdate() {
    }
  </script>
  
<div class={`fixed top-20 bottom-10 right-4 h-auto rounded-2xl transition-transform duration-300 ease-in-out z-50 ${showProfile ? 'translate-x-0' : 'translate-x-full'}`}>
  <!-- Profile content goes here -->
  <section class="border-gray-100 col-span-full flex-1 items-center">
    
    <form class="z-10 mx-auto rounded-xl border-2 border-primary-500 bg-slate-100 border shadow p-4 md:w-96 md:px-5" on:submit|preventDefault={handleUpdate}>
      <h1 class="pt-1 text-center text-lg font-bold text-primary-500">DriftConfig</h1>
      <p class="mb-1 text-gray-500 text-xs text-center">Current drift configuration</p>
      
      <div class="grid justify-items-center">
        <button type="submit" class="btn bg-primary-500 text-white rounded-lg md:w-72 justify-self-center mb-2">
          <span>Update</span>
        </button>
      </div>
    </form>
  </section>
</div>