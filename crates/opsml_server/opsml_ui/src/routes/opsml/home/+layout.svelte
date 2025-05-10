
<script lang="ts">
    let { children } = $props();
</script>

<div class="h-full w-full overflow-y-auto">
    {@render children()}
</div>