
<script lang="ts">
  let { children } = $props();
</script>

<div class="h-full overflow-auto">
  {@render children()}
</div>
