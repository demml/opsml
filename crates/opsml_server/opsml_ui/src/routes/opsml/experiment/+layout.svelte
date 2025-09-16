<script lang="ts">
    let { children } = $props();
    import Sidebar from "$lib/components/nav/Sidebar.svelte";
</script>

<div class="h-full">
  <Sidebar>
      {@render children()}
  </Sidebar>
</div>
