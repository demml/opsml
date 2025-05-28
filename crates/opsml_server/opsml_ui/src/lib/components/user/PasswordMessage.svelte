<script lang="ts">

import {OctagonAlert } from 'lucide-svelte';
let { message = 'unset'} = $props();

</script>

<div class="card p-4 border-2 border-error-500 max-w-screen-lg">

   <div class="flex flex-row pb-3 justify-center items-center gap-2">
      <OctagonAlert color="#C64142"/>
      <p class="text-secondary-700">Password Reset</p>
   </div>
  
   <div class="flex justify-center items-center">
      <p class="text-md text-secondary-700">{message}</p>
  </div>

</div>