<script lang="ts">
    let { children } = $props();
</script>

<div class="min-h-screen flex flex-col bg-surface-50">
  <div class="flex-1 overflow-auto">
    {@render children()}
  </div>
</div>