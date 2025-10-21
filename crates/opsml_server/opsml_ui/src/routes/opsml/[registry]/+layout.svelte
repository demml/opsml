<script lang="ts">
    let { children } = $props();
    import Sidebar from "$lib/components/nav/Sidebar.svelte";
    import { page } from '$app/state';
</script>

<div>
  <Sidebar>
    {#key page.params.registry}
      {@render children()}
    {/key}
  </Sidebar>
</div>
