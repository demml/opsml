<script lang="ts">
    let { children } = $props();
    import Sidebar from "$lib/components/nav/Sidebar.svelte";
    import { page } from '$app/stores';
</script>

<div>
  <Sidebar>
      {#key $page.params.card}
          {@render children()}
      {/key}
  </Sidebar>
</div>
