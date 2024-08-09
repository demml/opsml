<script lang="ts">

import Fa from "svelte-fa";
import { faExclamationTriangle } from "@fortawesome/free-solid-svg-icons";

export let errorMessage: string = '';

</script>

<aside class="mb-10 alert mx-auto shadow rounded-2xl bg-rose-500 md:w-1/3 items-center text-white">
  <!-- Icon -->
  <div>
      <Fa size='2x' icon={faExclamationTriangle} color="#ffffff" />
  </div>
  <!-- Message -->
  <div class="alert-message">
      <h3 class="h4">Problem Encountered</h3>
      <p class="text-sm">{errorMessage}</p>
  </div>
  <!-- Actions -->
</aside>