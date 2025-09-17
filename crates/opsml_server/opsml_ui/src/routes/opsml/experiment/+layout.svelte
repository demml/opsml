<script lang="ts">
    let { children } = $props();
    import Sidebar from "$lib/components/nav/Sidebar.svelte";
</script>

<div>
  <Sidebar>
      {@render children()}
  </Sidebar>
</div>
