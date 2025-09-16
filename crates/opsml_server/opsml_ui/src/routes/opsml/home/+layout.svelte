
<script lang="ts">
    let { children } = $props();
    import Sidebar from "$lib/components/nav/Sidebar.svelte";
</script>

<div class="h-full overflow-auto">
  <Sidebar>
      {@render children()}
  </Sidebar>
</div>