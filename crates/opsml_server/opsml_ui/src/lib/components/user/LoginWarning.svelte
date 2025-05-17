<script lang="ts">

import {OctagonAlert } from 'lucide-svelte';
let { errorMessage = 'unset'} = $props();

</script>

<aside class="mb-10 alert mx-auto shadow rounded-2xl bg-rose-500 md:w-1/3 items-center text-white">
  <!-- Icon -->
  <div>
      <OctagonAlert color="#ffffff" />
  </div>
  <!-- Message -->
  <div class="alert-message">
      <h3 class="h4">Problem Encountered</h3>
      <p class="text-sm">{errorMessage}</p>
  </div>
  <!-- Actions -->
</aside>