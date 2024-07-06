<script lang="ts">

	export let searchTerm;
  export let placeholder: string = "Filter artifacts";


</script>



<div class="search-bar">

  <input  class="h-7 rounded-full w-full border border-gray-200/70 bg-white pl-2 text-md placeholder-gray-400 ring-0 focus:outline-primary-500" 
          autocomplete="off" 
          placeholder={placeholder}
          type="text"
          bind:value={searchTerm}
          on:input
          on:keydown />
</div>