
<script lang="ts">
	import { type ModalStore} from '@skeletonlabs/skeleton';
  import { authManager } from '$lib/scripts/auth/authManager';
  import { goto } from '$app/navigation';
  import type { SvelteComponent } from 'svelte';

	export let modalStore: ModalStore;
  export let parent: SvelteComponent;
  

 
	function logOutHandler(): void {
    parent.onClose();
    authManager.logout();
    goto('/opsml/auth/login');
	}


</script>

{#if $modalStore[0]}

  <div class="modal block overflow-y-auto bg-surface-100-800-token w-fit h-auto p-4 space-y-4 rounded-container-token shadow-xl">
    <header class="modal-header text-2xl font-bold text-darkpurple">Usage</header> 
    <article class="modal-body max-h-[200px] overflow-hidden">Are you sure you want to sign out of your account?</article> 
    <footer class="modal-footer flex justify-end space-x-2">
      <button class="btn variant-filled" on:click={logOutHandler}>
        Logout
      </button>
    </footer>
  </div>

{/if}

