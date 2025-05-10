<script lang="ts">
    let { children } = $props();
</script>

<div class="h-screen flex flex-col">
  <div class="flex-1 overflow-auto">
    {@render children()}
  </div>
</div>