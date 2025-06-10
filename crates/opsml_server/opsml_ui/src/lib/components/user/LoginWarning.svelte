<script lang="ts">

import {OctagonAlert } from 'lucide-svelte';
let { errorMessage = 'unset'} = $props();

</script>

<div class="card p-4 border-2 border-error-500 max-w-screen-lg">

   <div class="flex flex-row pb-3 justify-center items-center gap-2">
      <OctagonAlert color="#C64142"/>
      <p class="text-error-700">Problem Encountered</p>
   </div>
  
   <div class="flex justify-center items-center">
      <p class="text-md text-error-700 text-sm">{errorMessage}</p>
  </div>

</div>