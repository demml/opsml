<script lang="ts">

  import { goto } from '$app/navigation';
  import { CommonPaths } from '$lib/scripts/types';

  /** @type {import('./$types').PageData} */
	export let data;

  export let error: string;
  error = data.error;

  function navigateToHome() {
    goto(CommonPaths.LOGIN);
  }

</script>

<div class="flex min-h-screen">
  <div class="error-container">
    <div class="error-content">
      <h1>Oops!</h1>
      <p>{error}</p>
      <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white text-xs" on:click={() => navigateToHome() }>Show</button>
    </div>
  </div>
</div>